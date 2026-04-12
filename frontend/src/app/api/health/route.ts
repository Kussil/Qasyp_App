export async function GET() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/health`);
    const data = await res.json();
    return Response.json(data);
  } catch {
    return Response.json({ status: "error" }, { status: 503 });
  }
}
