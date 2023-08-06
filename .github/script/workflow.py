from typing import Literal, Optional, get_type_hints
import os
import json
from pathlib import Path
import sys


def github_context(context: dict) -> tuple[None, str]:
    _ = context.pop("token")
    payload_data = context.pop("event")
    context_details = _details(
        content=_codeblock(content=json.dumps(dict(sorted(context.items())), indent=4), language="json"),
        summary="🖥 GitHub Context",
    )
    payload_details = _details(
        content=_codeblock(content=json.dumps(dict(sorted(payload_data.items())), indent=4), language="json"),
        summary="🖥 Event Payload",
    )
    return None, f"{context_details}\n{payload_details}"


def metadata(cache_hit: bool, force_update: str, metadata_filepath: str) -> tuple[None, str]:
    force_update_emoji = "✅" if force_update == "all" else ("❌" if force_update == "none" else "☑️")
    cache_hit_emoji = "✅" if cache_hit else "❌"
    if not cache_hit or force_update == "all":
        result = "Updated all metadata"
    elif force_update == "core":
        result = "Updated core metadata but loaded API metadata from cache"
    elif force_update == "none":
        result = "Loaded all metadata from cache"
    else:
        raise ValueError(f"Unknown force_update value: {force_update}")
    with open(metadata_filepath) as f:
        metadata = json.load(f)
    metadata = _details(
        content=_codeblock(content=json.dumps(metadata, indent=4), language="json"),
        summary="🖥 Metadata"
    )
    log = f"""
- {force_update_emoji}  Force update (input: {force_update})
- {cache_hit_emoji}  Cache hit
- ➡️ {result}
<br>
{metadata}
"""
    return None, log


def changed_files(categories: dict, total: dict) -> tuple[dict, str]:
    """
    Parse outputs from `actions/changed-files` action.

    This is used in the `repo_changed_files.yaml` workflow.
    It parses the outputs from the `actions/changed-files` action and
    creates a new output variable `json` that contains all the data,
    and writes a job summary.
    """
    # Parse and clean outputs
    sep_groups = dict()
    group_summary_str = ""
    for item_name, val in categories.items():
        group_name, attr = item_name.split("_", 1)
        group = sep_groups.setdefault(group_name, dict())
        group[attr] = val
    for group_name, group_attrs in sep_groups.items():
        sep_groups[group_name] = dict(sorted(group_attrs.items()))
        group_summary_str += (
            f"- {'✅' if group_attrs['any_modified'] == 'true' else '❌'}  {group_name}\n"
        )
    total = dict(sorted(total.items()))
    all_groups = {"all": total} | sep_groups
    file_list = "\n".join(sorted(total["all_changed_and_modified_files"].split()))
    # Write job summary
    changed_files = _details(
        content=_codeblock(content=file_list, language="bash"),
        summary="🖥 Changed Files",
    )
    details = _details(
        content=_codeblock(content=json.dumps(all_groups, indent=4), language="json"),
        summary="🖥 Details",
    )
    log = f"""
#### Modified Categories
{group_summary_str}

{changed_files}
{details}
    """
    return {"json": json.dumps(all_groups)}, log


def package_build_sdist() -> tuple[dict, str]:
    filename = list((Path.cwd() / "dist").glob("*.tar.gz"))[0]
    dist_name = filename.stem.removesuffix(".tar.gz")
    package_name, version = dist_name.rsplit("-", 1)
    output = {"package-name": package_name, "package-version": version}
    log = f"""
- Package Name: `{package_name}`
- Package Version: `{version}`
- Filename: `{filename.name}`
"""
    return output, log


def package_publish_pypi(
        package_name: str, package_version: str, platform_name: str, dist_path: str = "dist"
) -> tuple[dict, str]:
    download_url = {
        "PyPI": "https://pypi.org/project",
        "TestPyPI": "https://test.pypi.org/project",
    }
    upload_url = {
        "PyPI": "https://upload.pypi.org/legacy/",
        "TestPyPI": "https://test.pypi.org/legacy/",
    }
    outputs = {
        "download_url": f"{download_url[platform_name]}/{package_name}/{package_version}",
        "upload_url": upload_url[platform_name],
    }

    dists = "\n".join([path.name for path in list(Path(dist_path).glob("*.*"))])
    dist_files = _details(
        content=_codeblock(content=dists, language="bash"),
        summary="🖥 Distribution Files",
    )
    log = f"""
- Package Name: `{package_name}`
- Package Version: `{package_version}`
- Platform: `{platform_name}`
- {dist_files}
- Download URL: `{outputs["download_url"]}`
"""
    return outputs, log


def _details(content: str, summary: str = "Details") -> str:
    text = f"""
<details>
<summary>{summary}</summary>

{content}

</details>
"""
    return text


def _codeblock(content: str, language: str = "") -> str:
    text = f"""
```{language}
{content}
```
"""
    return text


if __name__ == "__main__":

    def read_input(job_id: str) -> dict:
        """
        Parse inputs from environment variables.
        """
        params = get_type_hints(globals()[job_id])
        args = {}
        if not params:
            return args
        params.pop("return", None)
        for name, typ in params.items():
            param_env_name = f"RD_{name.upper()}"
            val = os.environ.get(param_env_name)
            if val is None:
                print(f"ERROR: Missing input: {param_env_name}")
                sys.exit(1)
            if typ is str:
                args[name] = val
            elif typ is bool:
                args[name] = val.lower() == "true"
            elif typ is dict:
                args[name] = json.loads(val, strict=False)
            else:
                print(f"ERROR: Unknown input type: {typ}")
                sys.exit(1)
        return args

    def write_output(values: dict) -> Optional[dict]:
        print("OUTPUTS:")
        print("--------")
        print(values)
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            for name, value in values.items():
                print(f"{name.replace('_', '-')}={value}", file=fh)
        return

    def write_summary(content: str) -> None:
        print("SUMMARY:")
        print("--------")
        print(content)
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            print(content, file=fh)
        return

    job_id = os.environ["GITHUB_JOB"].replace('-', '_')
    kwargs = read_input(job_id=job_id)
    try:
        outputs, summary = globals()[job_id](**kwargs)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    if outputs:
        write_output(values=outputs)
    if summary:
        write_summary(content=summary)
