"use client";
import React, { useState } from "react";
import Link from "next/link";

// Mock suggestion data structure
interface Suggestion {
  id: number;
  section: string;
  suggestion: string;
  status: "pending" | "approved" | "rejected" | "edited";
  editedText?: string;
  file_path?: string;
  line_number?: number;
}

interface UpdateResult {
  message: string;
  success: Array<{ suggestion_id: number; file_path: string; message: string }>;
  errors: Array<{ suggestion_id: number; error: string }>;
  backups: string[];
}

const DocUpdatePage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updateResult, setUpdateResult] = useState<UpdateResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setUpdateResult(null);

    try {
      const response = await fetch(
        "http://fastapi_backend:8000/doc-updates/suggest",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ query }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get suggestions");
      }

      const data = await response.json();
      const suggestionsWithStatus = data.suggestions.map((s: any) => ({
        ...s,
        status: "pending" as const,
      }));

      setSuggestions(suggestionsWithStatus);
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = (id: number) => {
    setSuggestions((suggestions: Suggestion[]) =>
      suggestions.map((s: Suggestion) =>
        s.id === id ? { ...s, status: "approved", editedText: undefined } : s
      )
    );
  };

  const handleReject = (id: number) => {
    setSuggestions((suggestions: Suggestion[]) =>
      suggestions.map((s: Suggestion) =>
        s.id === id ? { ...s, status: "rejected", editedText: undefined } : s
      )
    );
  };

  const handleEdit = (id: number) => {
    setSuggestions((suggestions: Suggestion[]) =>
      suggestions.map((s: Suggestion) =>
        s.id === id ? { ...s, status: "edited", editedText: s.suggestion } : s
      )
    );
  };

  const handleEditChange = (id: number, value: string) => {
    setSuggestions((suggestions: Suggestion[]) =>
      suggestions.map((s: Suggestion) =>
        s.id === id ? { ...s, editedText: value } : s
      )
    );
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setUpdateResult(null);

    try {
      const approvedSuggestions = suggestions.filter(
        (s: Suggestion) => s.status === "approved" || s.status === "edited"
      );

      const response = await fetch("/api/doc-updates/apply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          suggestions: approvedSuggestions.map((s) => ({
            id: s.id,
            section: s.section,
            suggestion: s.status === "edited" ? s.editedText : s.suggestion,
            file_path: s.file_path,
            line_number: s.line_number,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to apply updates");
      }

      const data = await response.json();
      setUpdateResult(data);

      // Reset form only if all updates were successful
      if (data.errors.length === 0) {
        setQuery("");
        setSubmitted(false);
        setSuggestions([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const canSave = suggestions.some(
    (s: Suggestion) => s.status === "approved" || s.status === "edited"
  );

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">AI Documentation Updater</h1>
      <form onSubmit={handleSubmit} className="mb-8">
        <label htmlFor="query" className="block text-lg font-medium mb-2">
          Describe your documentation update:
        </label>
        <textarea
          id="query"
          className="w-full border rounded p-3 mb-4 min-h-[80px] focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="E.g. We don't support agents as_tool anymore, other agents should only be invoked via handoff"
          required
          disabled={loading}
        />
        <button
          type="submit"
          className={`px-6 py-2 rounded text-white transition ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
          disabled={loading}
        >
          {loading ? "Getting Suggestions..." : "Get Suggestions"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-6">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {updateResult && (
        <div className="bg-gray-50 border rounded p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Update Results</h2>

          <div className="mb-4">
            <p className="text-green-600 font-medium">{updateResult.message}</p>
          </div>

          {updateResult.success.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-green-700 mb-2">
                ✅ Successful Updates:
              </h3>
              <ul className="space-y-1">
                {updateResult.success.map((item, index) => (
                  <li key={index} className="text-sm text-green-600">
                    • {item.file_path}: {item.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {updateResult.errors.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-red-700 mb-2">❌ Errors:</h3>
              <ul className="space-y-1">
                {updateResult.errors.map((item, index) => (
                  <li key={index} className="text-sm text-red-600">
                    • Suggestion {item.suggestion_id}: {item.error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {updateResult.backups.length > 0 && (
            <div>
              <h3 className="font-medium text-blue-700 mb-2">
                💾 Backups Created:
              </h3>
              <ul className="space-y-1">
                {updateResult.backups.map((backup, index) => (
                  <li key={index} className="text-sm text-blue-600">
                    • {backup.split("/").pop()}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {submitted && (
        <div className="bg-gray-50 border rounded p-6">
          <h2 className="text-xl font-semibold mb-4">Suggestions</h2>
          {suggestions.length === 0 ? (
            <p className="text-gray-500">
              No suggestions found for your query.
            </p>
          ) : (
            <ul className="space-y-6">
              {suggestions.map((s) => (
                <li key={s.id} className="border rounded p-4 bg-white">
                  <div className="mb-2 text-sm text-gray-500">
                    Section: {s.section}
                    {s.file_path && (
                      <span className="ml-2 text-xs">({s.file_path})</span>
                    )}
                  </div>
                  {s.status === "edited" ? (
                    <textarea
                      className="w-full border rounded p-2 mb-2 min-h-[60px]"
                      value={s.editedText}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                        handleEditChange(s.id, e.target.value)
                      }
                    />
                  ) : (
                    <div className="mb-2">{s.suggestion}</div>
                  )}
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className={`px-3 py-1 rounded text-white ${s.status === "approved" ? "bg-green-600" : "bg-green-500 hover:bg-green-600"}`}
                      onClick={() => handleApprove(s.id)}
                      disabled={s.status === "approved"}
                    >
                      {s.status === "approved" ? "Approved" : "Approve"}
                    </button>
                    <button
                      type="button"
                      className={`px-3 py-1 rounded text-white ${s.status === "rejected" ? "bg-red-600" : "bg-red-500 hover:bg-red-600"}`}
                      onClick={() => handleReject(s.id)}
                      disabled={s.status === "rejected"}
                    >
                      {s.status === "rejected" ? "Rejected" : "Reject"}
                    </button>
                    <button
                      type="button"
                      className="px-3 py-1 rounded bg-yellow-500 text-white hover:bg-yellow-600"
                      onClick={() => handleEdit(s.id)}
                      disabled={s.status === "edited"}
                    >
                      {s.status === "edited" ? "Editing" : "Edit"}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
          <button
            type="button"
            className={`mt-8 w-full py-2 rounded text-white text-lg ${
              canSave && !loading
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-gray-400 cursor-not-allowed"
            }`}
            onClick={handleSave}
            disabled={!canSave || loading}
          >
            {loading ? "Saving..." : "Save Updates"}
          </button>
        </div>
      )}
    </div>
  );
};

export default DocUpdatePage;
