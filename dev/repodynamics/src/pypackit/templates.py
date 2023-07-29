from typing import Optional
from pathlib import Path
import re

import ruamel.yaml

from . import metadata


class Templates:

    def __init__(
            self,
            path_root: Optional[str | Path] = None,
            path_pathfile: Optional[str | Path] = None,
            path_cache: Optional[str | Path] = None,
            update_cache: bool = False,
    ):
        self.metadata = metadata(
            path_root=path_root,
            path_pathfile=path_pathfile,
            path_cache=path_cache,
            update_cache=update_cache,
        )
        self._path_root = Path(self.metadata['path']['abs']['root'])
        return

    def update_readme(self):
        pass

    def update_health_files(self):
        for filepath in Path(self.metadata['path']['abs']['meta']['template']['health_file']).glob("*.md"):
            target_path = self.metadata['path']['abs']['health_file'].get(filepath.stem.casefold())
            if not target_path:
                continue
            with open(filepath) as f:
                text = f.read()
            with open(Path(target_path) / filepath.name, "w") as f:
                f.write(text.format(metadata=self.metadata))

    def update_license(self):
        filename = self.metadata['project']['license'].lower().rstrip("+")
        with open(Path(self.metadata['path']['abs']['meta']['template']['license']) / f'{filename}.txt') as f:
            text = f.read()
        with open(self._path_root / 'LICENSE', "w") as f:
            f.write(text.format(metadata=self.metadata))
        return

    def update_package_init_docstring(self):
        filename = self.metadata['project']['license'].lower().rstrip("+")
        with open(Path(self.metadata['path']['abs']['meta']['template']['license']) / f'{filename}_notice.txt') as f:
            text = f.read()
        copyright_notice = text.format(metadata=self.metadata)
        docstring = f"""{self.metadata['project']['name']}

{self.metadata['project']['tagline']}

{self.metadata['project']['description']}

{copyright_notice}"""
        path_src = self._path_root / "src"
        path_package = path_src / self.metadata['package']['name']
        if not path_package.exists():
            package_dirs = [
                sub for sub in [sub for sub in path_src.iterdir() if sub.is_dir()]
                if "__init__.py" in [subsub.name for subsub in sub.iterdir()]
            ]
            if len(package_dirs) > 1:
                raise ValueError(
                    f"More than one package directory found in '{path_src}'."
                )
            package_dirs[0].rename(path_package)
        path_init = path_package / '__init__.py'
        with open(path_init) as f:
            text = f.read()
        docstring_pattern = r'(\"\"\")(.*?)(\"\"\")'
        match = re.search(docstring_pattern, text, re.DOTALL)
        if match:
            # Replace the existing docstring with the new one
            new_text = re.sub(docstring_pattern, rf'\1{docstring}\3', text, flags=re.DOTALL)
        else:
            # If no docstring found, add the new docstring at the beginning of the file
            new_text = f'\"\"\"\n{docstring}\n\"\"\"\n{text}'
        # Write the modified content back to the file
        with open(path_init, 'w') as file:
            file.write(new_text)
        return

    def update_codeowners(self):
        """

        Returns
        -------

        References
        ----------
        https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners#codeowners-syntax
        """
        max_len = max([len(entry['pattern']) for entry in self.metadata['maintainers']['pull_requests']])
        text = ""
        for entry in self.metadata['maintainers']['pull_requests']:
            reviewers = ' '.join([f'@{reviewer}' for reviewer in entry['reviewers']])
            text += f'{entry["pattern"]: <{max_len}}   {reviewers}\n'
        with open(Path(self.metadata['path']['abs']['health_file']['codeowners']) / 'CODEOWNERS', "w") as f:
            f.write(text)
        return

    def update_funding(self):
        """

        Returns
        -------

        References
        ----------
        https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository#about-funding-files
        """
        path_funding_file = self._path_root / '.github' / 'FUNDING.yml'
        if not self.metadata['project']['funding']:
            path_funding_file.unlink(missing_ok=True)
            return
        funding = dict()
        for funding_platform, users in self.metadata['project']['funding'].items():
            if funding_platform not in [
                'community_bridge',
                'github',
                'issuehunt',
                'ko_fi',
                'liberapay',
                'open_collective',
                'otechie',
                'patreon',
                'tidelift',
                'custom',
            ]:
                raise ValueError(f"Funding platform '{funding_platform}' is not recognized.")
            if funding_platform in ['github', 'custom']:
                if isinstance(users, list):
                    if len(users) > 4:
                        raise ValueError("The maximum number of allowed users is 4.")
                    flow_list = ruamel.yaml.comments.CommentedSeq()
                    flow_list.fa.set_flow_style()
                    flow_list.extend(users)
                    funding[funding_platform] = flow_list
                elif isinstance(users, str):
                    funding[funding_platform] = users
                else:
                    raise ValueError(
                        f"Users of the '{funding_platform}' funding platform must be either "
                        f"a string or a list of strings, but got {users}."
                    )
            else:
                if not isinstance(users, str):
                    raise ValueError(
                        f"User of the '{funding_platform}' funding platform must be a single string, "
                        f"but got {users}."
                    )
                funding[funding_platform] = users
        with open(path_funding_file, 'w') as f:
            ruamel.yaml.YAML().dump(funding, f)
        return

    def update_issue_forms(self):
        pass
