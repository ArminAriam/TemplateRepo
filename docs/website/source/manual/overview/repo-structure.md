# Repository Structure
Every {{pp_meta.name}} repository must conform to a specific directory structure.
For example, some directories must always be present in a specific location,
while some other directories must have a specific substructure, but their location is configurable.

### GitHub Directory
Every repository must contain a `./.github` directory,
i.e., a directory named `.github` located at the root (`./`) of the repository.
This is where GitHub looks for GitHub Actions workflow files
(`.yaml` files in the `./.github/workflows` directory) and other configuration files,
such as issue-, discussion-, and pull request templates.

When a repository is first initialized from the {{pp_meta.name}} template,
the `./.github` directory will only contain workflow files.
These are configurations that define the continuous integration and delivery (CI/CD)
pipelines of the repository, allowing the whole development and maintenance process of your project
to be automatically managed by {{pp_meta.name}}.
In general, you should never modify these files directly, since all configurations and data that
are specific to each project are read automatically from the repository's `meta` content (discussed below).
The only exception is when you want to add a new feature/functionality to your pipelines,
which is not covered by {{pp_meta.name}} and is completely orthogonal to its functionalities.

After the repository is configured, a number of other files and directories
will also be automatically added to the `./.github` directory,
including issue-, discussion-, and pull request templates, and other GitHub configuration files.
{{pp_meta.name}} also uses the `./.github` directory to store some of its own data and settings,
as well as configuration files for other external tools that are used by {{pp_meta.name}}.
You must never modify these files directly, as they are dynamic files that are automatically
generated and updated by {{pp_meta.name}} according to the repository's `meta` content.

### Meta Directory
The `meta` directory is the main control center of your repository,
where all configurations, metadata, and settings
for your GitHub repository (and its corresponding git repository),
package, website, development pipeline, and other tools are stored in one place.
When you apply a change to the repository's `meta` content and push it to the remote repository,
{{pp_meta.name}} will automatically apply the corresponding changes to entire repository and its content,
so that the repository is always in a consistent state with its `meta` content.
This is the main mechanism that {{pp_meta.name}} uses to manage your repository and project,
so you must never modify any configuration directly, but always through the `meta` content.

This directory is named `.meta` by default, and is located at the root of the repository.
You can change the name and location of your repository's `meta` directory,
but it must have a specific substructure, meaning that {{pp_meta.name}} will look for
specific files and directories in specific locations inside the `meta` directory
to read the corresponding configurations and data from.

### Source Directory
The `source` directory is where all source code of your package is stored.
{{pp_meta.name}} follows the
[Setuptools's src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout)
for package discovery.
This means that your `source` directory must contain a single top-level package directory,
which must at least contain a `__init__.py` file. The name of this top-level package directory
defines the import name of your package. You must never rename the top-level package directory directly;
instead, {{pp_meta.name}} will automatically rename it for you
when you change the package name in the `meta` content. {{pp_meta.name}} will also automatically
update all import statements in your source code to reflect the new package name.

In addition, the `source` directory must always be placed at the root of the repository,
but you can change its name via the `meta` content.
When the repository is first initialized, {{pp_meta.name}} will automatically create the `source` directory
(default: `src`) and the top-level package directory, along with the top-level `__init__.py` file.
Note that the docstring of the top-level `__init__.py` file is also dynamic. Therefore, while you can
change the content of the `__init__.py` file, you must never change the docstring directly, but always
through the `meta` content.