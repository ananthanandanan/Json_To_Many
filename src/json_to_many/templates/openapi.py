"""OpenAPI 3.0/3.1 → Markdown renderer.

Dispatched from ``JsonToMarkdown`` when ``template="openapi"``. Produces a
single readable Markdown document: info block, authentication, endpoints
grouped by tag, and a trailing "Schemas" section that ``$ref`` links point
into (link-and-collect, so circular refs terminate).
"""

from __future__ import annotations

import json
import re
from typing import Any

from ..exceptions import JsonToManyError

# OpenAPI Path Item fields that are HTTP operations, in conventional order.
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head", "trace")

# Bucket for operations that carry no tag.
UNTAGGED = "Other"


class OpenApiTemplate:
    """Render an OpenAPI document to Markdown.

    Instantiated with the parsed spec (a dict) and the merged converter
    options, then ``.render()`` returns the Markdown string. ``endpoint_count``
    is populated during rendering for ``ConversionStats``.
    """

    def __init__(self, data: Any, **options: Any) -> None:
        self.spec = data
        self.options = options
        self.lines: list[str] = []
        self._schemas: dict[str, Any] = {}
        self._needed: set[str] = set()  # schema names reached via $ref
        self.endpoint_count = 0

    # -- public ------------------------------------------------------------

    def render(self) -> str:
        self._validate()
        components = self.spec.get("components") or {}
        self._schemas = components.get("schemas") or {}
        self._render_info()
        self._render_auth()
        self._render_endpoints()
        self._render_schemas()
        # End on a single trailing newline (POSIX text-file convention); the
        # section emitters leave a trailing blank line between blocks.
        return "".join(self.lines).rstrip("\n") + "\n"

    # -- validation --------------------------------------------------------

    def _validate(self) -> None:
        if not isinstance(self.spec, dict):
            raise JsonToManyError(
                "openapi template expects an OpenAPI document (a JSON object), "
                f"got {type(self.spec).__name__}."
            )
        if "swagger" in self.spec:
            raise JsonToManyError(
                "Swagger 2.0 specs are not supported by the openapi template "
                "(only OpenAPI 3.0/3.1). Found a top-level 'swagger' key."
            )
        version = self.spec.get("openapi")
        if not version:
            raise JsonToManyError(
                "Input does not look like an OpenAPI document: missing the "
                "top-level 'openapi' version key."
            )
        if not str(version).startswith("3."):
            raise JsonToManyError(
                f"Unsupported OpenAPI version {version!r}; the openapi template "
                "supports 3.0 and 3.1."
            )

    # -- info / servers ----------------------------------------------------

    def _render_info(self) -> None:
        info = self.spec.get("info") or {}
        self.lines.append(f"# {info.get('title', 'API Reference')}\n\n")
        version = info.get("version")
        if version:
            self.lines.append(f"**Version:** {version}\n\n")
        description = info.get("description")
        if description:
            self.lines.append(f"{description}\n\n")
        servers = self.spec.get("servers") or []
        urls = [s for s in servers if isinstance(s, dict) and s.get("url")]
        if urls:
            self.lines.append("**Servers**\n\n")
            for s in urls:
                suffix = f" — {s['description']}" if s.get("description") else ""
                self.lines.append(f"- `{s['url']}`{suffix}\n")
            self.lines.append("\n")

    # -- authentication ----------------------------------------------------

    def _render_auth(self) -> None:
        components = self.spec.get("components") or {}
        schemes = components.get("securitySchemes") or {}
        if not schemes:
            return
        self.lines.append("## Authentication\n\n")
        self.lines.append("| Scheme | Type | Details |\n")
        self.lines.append("| --- | --- | --- |\n")
        for name, scheme in schemes.items():
            if isinstance(scheme, dict) and "$ref" in scheme:
                scheme = self._deref(scheme["$ref"]) or {}
            if not isinstance(scheme, dict):
                continue
            details = self._auth_details(scheme)
            self.lines.append(
                f"| {self._esc(name)} | {self._esc(scheme.get('type', ''))} | {details} |\n"
            )
        self.lines.append("\n")

    def _auth_details(self, scheme: dict) -> str:
        kind = scheme.get("type")
        if kind == "apiKey":
            return self._esc(f"{scheme.get('in', '')}: {scheme.get('name', '')}")
        if kind == "http":
            fmt = scheme.get("bearerFormat")
            label = scheme.get("scheme", "")
            return self._esc(label + (f" ({fmt})" if fmt else ""))
        if kind == "oauth2":
            flows = scheme.get("flows") or {}
            return self._esc("flows: " + ", ".join(flows.keys()))
        if kind == "openIdConnect":
            return self._esc(scheme.get("openIdConnectUrl", ""))
        return ""

    # -- endpoints ---------------------------------------------------------

    def _render_endpoints(self) -> None:
        paths = self.spec.get("paths") or {}
        groups: dict[str, list[tuple]] = {}
        order: list[str] = []

        # Seed tag order from the top-level `tags` array when present.
        for tag in self.spec.get("tags") or []:
            if isinstance(tag, dict) and tag.get("name") and tag["name"] not in groups:
                groups[tag["name"]] = []
                order.append(tag["name"])

        for path, item in paths.items():
            if not isinstance(item, dict):
                continue
            shared_params = item.get("parameters") or []
            for method in HTTP_METHODS:
                op = item.get(method)
                if not isinstance(op, dict):
                    continue
                tags = op.get("tags") or []
                tag = tags[0] if tags else UNTAGGED
                if tag not in groups:
                    groups[tag] = []
                    order.append(tag)
                groups[tag].append((path, method.upper(), op, shared_params))

        # "Other" always sorts last.
        if UNTAGGED in order:
            order = [t for t in order if t != UNTAGGED] + [UNTAGGED]

        descriptions = {
            t["name"]: t.get("description", "")
            for t in (self.spec.get("tags") or [])
            if isinstance(t, dict) and t.get("name")
        }

        for tag in order:
            ops = groups.get(tag)
            if not ops:
                continue
            self.lines.append(f"## {tag}\n\n")
            if descriptions.get(tag):
                self.lines.append(f"{descriptions[tag]}\n\n")
            for path, method, op, shared in ops:
                self._render_operation(path, method, op, shared)
                self.endpoint_count += 1

    def _render_operation(self, path, method, op, shared_params) -> None:
        self.lines.append(f"### {method} {path}\n\n")
        summary = op.get("summary")
        if summary:
            self.lines.append(f"{summary}\n\n")
        description = op.get("description")
        if description and description != summary:
            self.lines.append(f"{description}\n\n")
        if "security" in op:
            names = self._security_names(op["security"])
            self.lines.append(f"**Security:** {names or 'none (public)'}\n\n")

        params = list(shared_params) + list(op.get("parameters") or [])
        self._render_parameters(params)
        self._render_request_body(op.get("requestBody"))
        self._render_responses(op.get("responses"))

    def _security_names(self, security: Any) -> str:
        if not isinstance(security, list):
            return ""
        names: list[str] = []
        for requirement in security:
            if isinstance(requirement, dict):
                names.extend(requirement.keys())
        return ", ".join(dict.fromkeys(names))  # dedupe, preserve order

    def _render_parameters(self, params: list) -> None:
        resolved = [self._resolve_ref(p) for p in params]
        resolved = [p for p in resolved if isinstance(p, dict) and p.get("name")]
        if not resolved:
            return
        self.lines.append("**Parameters**\n\n")
        self.lines.append("| Name | In | Type | Required | Description |\n")
        self.lines.append("| --- | --- | --- | --- | --- |\n")
        for p in resolved:
            ptype = self._type_of(p.get("schema", {})) if p.get("schema") else ""
            required = "yes" if p.get("required") else "no"
            self.lines.append(
                f"| {self._esc(p.get('name', ''))} | {self._esc(p.get('in', ''))} "
                f"| {ptype} | {required} | {self._esc(p.get('description', ''))} |\n"
            )
        self.lines.append("\n")

    def _render_request_body(self, request_body: Any) -> None:
        request_body = self._resolve_ref(request_body)
        if not isinstance(request_body, dict):
            return
        media = self._pick_media(request_body.get("content") or {})
        if media is None:
            return
        mtype, mobj = media
        type_label = self._type_of(mobj.get("schema", {}))
        required = " (required)" if request_body.get("required") else ""
        self.lines.append(f"**Request body** (`{mtype}`){required}: {type_label}\n\n")
        if request_body.get("description"):
            self.lines.append(f"{request_body['description']}\n\n")
        self._render_example(mobj, mobj.get("schema", {}))

    def _render_responses(self, responses: Any) -> None:
        if not isinstance(responses, dict) or not responses:
            return
        self.lines.append("**Responses**\n\n")
        self.lines.append("| Status | Description | Schema |\n")
        self.lines.append("| --- | --- | --- |\n")
        examples: list[tuple] = []
        for status, response in responses.items():
            response = self._resolve_ref(response)
            if not isinstance(response, dict):
                continue
            schema_label = "—"
            media = self._pick_media(response.get("content") or {})
            if media:
                _, mobj = media
                schema = mobj.get("schema", {})
                schema_label = self._type_of(schema) or "—"
                examples.append((status, mobj, schema))
            self.lines.append(
                f"| {self._esc(status)} | {self._esc(response.get('description', ''))} "
                f"| {schema_label} |\n"
            )
        self.lines.append("\n")
        for status, mobj, schema in examples:
            self._render_example(mobj, schema, label=f"Example · {status}")

    def _render_example(
        self, media_obj: Any, schema: Any, label: str = "Example"
    ) -> None:
        example = None
        if isinstance(media_obj, dict):
            if "example" in media_obj:
                example = media_obj["example"]
            elif isinstance(media_obj.get("examples"), dict):
                for named in media_obj["examples"].values():
                    if isinstance(named, dict) and "value" in named:
                        example = named["value"]
                        break
        if example is None and isinstance(schema, dict):
            example = schema.get("example")
        if example is None:
            return
        self.lines.append(f"**{label}**\n\n")
        self.lines.append("```json\n")
        self.lines.append(json.dumps(example, indent=2, ensure_ascii=False))
        self.lines.append("\n```\n\n")

    # -- schemas (link-and-collect) ---------------------------------------

    def _render_schemas(self) -> None:
        defined = set(self._schemas)
        if not (self._needed & defined):
            return
        self.lines.append("## Schemas\n\n")
        done: set[str] = set()
        # The worklist grows as _type_of() discovers nested refs; each name
        # renders at most once, so circular refs terminate.
        while True:
            remaining = (self._needed & defined) - done
            if not remaining:
                break
            name = sorted(remaining)[0]
            done.add(name)
            self._render_one_schema(name, self._schemas[name])

    def _render_one_schema(self, name: str, schema: Any) -> None:
        self.lines.append(f"### {name}\n\n")
        if not isinstance(schema, dict):
            return
        if schema.get("description"):
            self.lines.append(f"{schema['description']}\n\n")
        properties = schema.get("properties")
        if isinstance(properties, dict) and properties:
            required = set(schema.get("required") or [])
            self.lines.append("| Field | Type | Required | Description |\n")
            self.lines.append("| --- | --- | --- | --- |\n")
            for fname, fschema in properties.items():
                ftype = self._type_of(fschema) if isinstance(fschema, dict) else ""
                fdesc = (
                    fschema.get("description", "") if isinstance(fschema, dict) else ""
                )
                req = "yes" if fname in required else "no"
                self.lines.append(
                    f"| {self._esc(fname)} | {ftype} | {req} | {self._esc(fdesc)} |\n"
                )
            self.lines.append("\n")
        else:
            self.lines.append(f"Type: {self._type_of(schema) or 'object'}\n\n")
            if "enum" in schema:
                vals = ", ".join(f"`{v}`" for v in schema["enum"])
                self.lines.append(f"Allowed values: {vals}\n\n")

    # -- type rendering ----------------------------------------------------

    def _type_of(self, schema: Any) -> str:
        """A Markdown type label for a schema dict, queueing any ``$ref``."""
        if not isinstance(schema, dict):
            return ""
        if "$ref" in schema:
            return self._ref_link(schema["$ref"])
        for key, joiner in (("allOf", " & "), ("oneOf", " or "), ("anyOf", " or ")):
            if isinstance(schema.get(key), list):
                parts = [self._type_of(s) for s in schema[key]]
                return joiner.join(p for p in parts if p)
        kind = schema.get("type")
        if isinstance(kind, list):  # OAS 3.1 type arrays, e.g. ["string", "null"]
            non_null = [k for k in kind if k != "null"]
            label = " or ".join(non_null) if non_null else "null"
            if "null" in kind and non_null:
                label += " (nullable)"
            return label
        if kind == "array":
            inner = self._type_of(schema.get("items", {})) or "any"
            return f"array of {inner}"
        if kind == "object" or (kind is None and "properties" in schema):
            return "object"
        fmt = schema.get("format")
        if kind and fmt:
            return f"{kind} ({fmt})"
        if kind:
            return kind
        if "enum" in schema:
            return "enum"
        return "any"

    def _ref_link(self, ref: str) -> str:
        name = ref.rsplit("/", 1)[-1]
        if "/components/schemas/" in ref:
            self._needed.add(name)
            return f"[{name}](#{self._anchor(name)})"
        return f"`{name}`"

    # -- helpers -----------------------------------------------------------

    def _resolve_ref(self, node: Any) -> Any:
        """Resolve a one-level ``$ref`` wrapper (parameters, bodies, responses)."""
        if isinstance(node, dict) and "$ref" in node:
            return self._deref(node["$ref"]) or node
        return node

    def _deref(self, ref: str) -> Any:
        """Resolve a local JSON pointer (``#/a/b/c``) against the spec."""
        if not isinstance(ref, str) or not ref.startswith("#/"):
            return None
        node: Any = self.spec
        for part in ref[2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return None
        return node

    def _pick_media(self, content: Any) -> tuple[str, dict] | None:
        if not isinstance(content, dict) or not content:
            return None
        if "application/json" in content:
            return "application/json", content["application/json"]
        key = next(iter(content))
        return key, content[key]

    @staticmethod
    def _anchor(text: str) -> str:
        """GitHub-style heading slug: lowercase, punctuation stripped."""
        slug = re.sub(r"[^\w\- ]", "", str(text).strip().lower())
        return slug.replace(" ", "-")

    @staticmethod
    def _esc(value: Any) -> str:
        """Make a value safe inside a GFM table cell."""
        if value is None:
            return ""
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
