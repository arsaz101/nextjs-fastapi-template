import React, { useState } from "react";

// Mock suggestion data structure
interface Suggestion {
  id: number;
  section: string;
  suggestion: string;
  status: "pending" | "approved" | "rejected" | "edited";
  editedText?: string;
}

const mockSuggestions: Suggestion[] = [
  {
    id: 1,
    section: "Introduction",
    suggestion:
      "Remove mention of agents as_tool. Clarify that agents should only be invoked via handoff.",
    status: "pending",
  },
  {
    id: 2,
    section: "Usage",
    suggestion:
      "Update usage example to remove as_tool and use handoff instead.",
    status: "pending",
  },
];

const DocUpdatePage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    // Simulate backend response
    setSuggestions(mockSuggestions);
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

  const handleSave = () => {
    // TODO: Send approved/edited suggestions to backend
    alert("Saved! (This would send data to backend)");
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
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
        >
          Get Suggestions
        </button>
      </form>
      {submitted && (
        <div className="bg-gray-50 border rounded p-6">
          <h2 className="text-xl font-semibold mb-4">Suggestions</h2>
          {suggestions.length === 0 ? (
            <p className="text-gray-500">
              (Suggestions will appear here after backend integration.)
            </p>
          ) : (
            <ul className="space-y-6">
              {suggestions.map((s) => (
                <li key={s.id} className="border rounded p-4 bg-white">
                  <div className="mb-2 text-sm text-gray-500">
                    Section: {s.section}
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
            className={`mt-8 w-full py-2 rounded text-white text-lg ${canSave ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-400 cursor-not-allowed"}`}
            onClick={handleSave}
            disabled={!canSave}
          >
            Save Updates
          </button>
        </div>
      )}
    </div>
  );
};

export default DocUpdatePage;
