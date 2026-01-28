---
date: "{{ .Date }}"
draft: true
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
---

{{< callout  >}}
이 페이지의 핵심 내용을 한두 문장으로 요약해 주세요. 이 요약은 독자가 페이지 전체를 읽지 않고도 핵심을 파악하는 데 도움을 줍니다.
{{< /callout >}}
