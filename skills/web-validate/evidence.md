# Attaching evidence

Say in one line what each screenshot shows.

**GitHub:** no upload API for images; give the user the file paths, or describe them in a comment.

**Azure DevOps work item:**

```bash
TOK=$(az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv)
URL=$(curl -s -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/octet-stream" \
  --data-binary @shot.png "https://dev.azure.com/<org>/<project>/_apis/wit/attachments?fileName=shot.png&api-version=7.1" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])")
az boards work-item update --id <id> --org https://dev.azure.com/<org> \
  --discussion "What this shows.<br><img src=\"$URL\">"
```

**Azure DevOps pull request:** same upload to
`…/_apis/git/repositories/<repo>/pullRequests/<id>/attachments/<name>.png`, then `![name](<url>)`
in the description.

**No browser at all:** weaker evidence, labelled as such: follow the site's JS bundles from its
HTML with `curl` and grep for the strings the change added or removed.
