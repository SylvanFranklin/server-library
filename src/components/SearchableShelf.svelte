<script>
  export let items = [];
  export let placeholder = "Search this shelf";
  export let emptyMessage = "Nothing here yet.";
  export let searchLabel = "Search";

  let query = "";

  $: normalizedQuery = query.trim().toLowerCase();
  $: filteredItems = items.filter((item) => {
    if (!normalizedQuery) return true;

    const haystack = [
      item.title,
      item.subtitle,
      item.meta,
      item.kindLabel,
      item.username
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return haystack.includes(normalizedQuery);
  });
</script>

<div class="shelf-search">
  <label class="search-label">
    <span>{searchLabel}</span>
    <input bind:value={query} type="search" placeholder={placeholder} />
  </label>
</div>

{#if filteredItems.length}
  <ul class="media-list">
    {#each filteredItems as item}
      <li class="media-card">
        {#if item.imageUrl && !(item.isPosterFallback && item.imageUrl.startsWith("data:image/svg+xml"))}
          <img
            class={`media-art ${item.wide ? "media-art-wide" : ""}`}
            src={item.imageUrl}
            alt={item.imageAlt || item.title}
            loading="lazy"
          />
        {:else if item.isPosterFallback}
          <div class="media-art poster-fallback">
            <span class="poster-label">Movie Poster</span>
            <strong>{item.title}</strong>
            {#if item.posterText}
              <span>{item.posterText}</span>
            {/if}
          </div>
        {:else}
          <div class={`media-art ${item.wide ? "media-art-wide" : ""} media-art-placeholder`} aria-hidden="true">
            {item.placeholderLabel || "No image"}
          </div>
        {/if}

        <div>
          {#if item.href}
            <strong><a href={item.href}>{item.title}</a></strong>
          {:else}
            <strong>{item.title}</strong>
          {/if}
          {#if item.subtitle}
            <span> {item.subtitle}</span>
          {/if}
          {#if item.meta}
            <div class="meta">{item.meta}</div>
          {/if}
        </div>
      </li>
    {/each}
  </ul>
{:else}
  <p>{emptyMessage}</p>
{/if}
