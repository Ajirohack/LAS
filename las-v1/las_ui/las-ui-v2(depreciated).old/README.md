# LAS UI v2

This is the Next.js frontend for the Local Agentic System (LAS).

**Location:** This frontend is located at `gemini_build/las_ui/las-ui-v2/` and connects to the LAS backend at `gemini_build/las_core/`.

**Integration:** The backend references this frontend in `docker-compose.yml` for containerized deployment.

## Getting Started

Since this project was initialized manually, you need to install the dependencies first.

1. Make sure you have Node.js installed.
2. Run the following command in this directory:

```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Tech Stack

* **Framework:** Next.js 14
* **Language:** TypeScript
* **Styling:** Tailwind CSS
* **Components:** Shadcn/ui (Radix UI)
* **Icons:** Lucide React
