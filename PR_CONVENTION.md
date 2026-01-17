# Pull Request Convention (PR Convention)

To ensure consistent code reviews and smooth collaboration, please follow the guidelines below when creating Pull Requests.

## 1. PR Title Rules

The PR title should follow the same tags as defined in the Commit Convention.

`[type] PR Subject`

- Example: `[feat] implement notion workspace integration`
- Example: `[fix] resolve redirection error in login guard`

---

## 2. PR Description Template

Include the following sections in your PR description so that reviewers can easily understand the changes.

```markdown
## 📝 Summary
<!-- Provide a concise summary of the core changes in this PR. -->

## 🚀 Key Changes
<!-- Describe the changes in detail. A checklist format is recommended. -->
- [ ] Task 1
- [ ] Task 2

## 📸 Screenshots
<!-- For UI changes, please attach before/after screenshots or GIFs. -->

## 🔍 Review Points
<!-- Mention specific parts of the code you want reviewers to focus on or any points of concern. -->

## 🔗 Related Issues
<!-- Link resolved issues or related PR numbers. (e.g., Resolves #123) -->
```

---

## 3. PR & Review Guidelines

- **PR Size**: Keep each PR focused on a single feature or logical unit to make reviews more manageable.
- **Self Review**: Before requesting a review, go through your own code to check for unnecessary `console.log` statements or TODO comments.
- **Resolve Conflicts**: Ensure your PR is up-to-date with the base branch (e.g., `develop`) and is free of merge conflicts.
- **Approval Condition**: At least one approval from a reviewer is required before merging.
