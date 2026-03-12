import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";

const repo = process.env.GITHUB_REPOSITORY?.split("/")[1];
const owner = process.env.GITHUB_REPOSITORY_OWNER;
const isGithubActions = process.env.GITHUB_ACTIONS === "true";

export default defineConfig({
  output: "static",
  site: isGithubActions && owner ? `https://${owner}.github.io` : undefined,
  base: isGithubActions && repo ? `/${repo}/` : "/",
  integrations: [svelte()]
});
