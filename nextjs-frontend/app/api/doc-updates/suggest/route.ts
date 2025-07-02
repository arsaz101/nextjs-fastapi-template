import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward request to FastAPI backend
    const response = await fetch("http://localhost:8000/doc-updates/suggest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in doc-updates suggest API:", error);
    return NextResponse.json(
      { error: "Failed to get suggestions" },
      { status: 500 }
    );
  }
}
