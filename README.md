# <img width="48" height="48" alt="Stellody" src="public/favicon.ico" /> stellody-website

The `stellody.com` host for [Stellody](https://stellody.co.uk/), a local-first
FLAC music player. This repository holds a static copy of the Stellody site so
that the `.com` address reaches the product rather than a placeholder.

## Who this is for

Nobody, directly. It is infrastructure. If you want Stellody itself, go to
[stellody.co.uk](https://stellody.co.uk/); if you want its source, go to
[github.com/oernster/Stellody](https://github.com/oernster/Stellody).

This is NOT the canonical site and NOT where the site is authored. It carries no
application, no server, no forms and no analytics.

## Where the content comes from

The pages under `public/` are copied from `docs/` in the Stellody repository,
which is what GitHub Pages serves at `stellody.co.uk`. That copy is the source
of truth; edits belong there and arrive here by being copied again.

Two files are deliberately NOT copied across:

| File | Why it stays behind |
| --- | --- |
| `CNAME` | It names the GitHub Pages custom domain; it means nothing on Render |
| `sitemap.xml` | The primary host owns the sitemap, so this mirror does not offer a competing one |

Every page keeps its `canonical`, `og:url` and `og:image` pointing at
`https://stellody.co.uk/`. That is deliberate: it tells search engines which
host owns the pages, so the two do not compete for the same content. Do not
repoint them at this host.

## Stack

| Concern | Choice |
| --- | --- |
| Content | Plain HTML, CSS and images |
| Build | None |
| Runtime | None |
| Hosting | Render static site, per `render.yaml` |

## Serving it locally

Any static file server will do:

```
python -m http.server 8000 --directory public
```

Then open `http://localhost:8000/`.

## Deploying

`render.yaml` declares a Render **static site** publishing `./public`. There is
no start command because there is no process to start.

## Licence

GPL-3.0. See [LICENSE](LICENSE).
