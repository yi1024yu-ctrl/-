# QC Report — 2026年5〜9月 胃がん・大腸がん・乳がん 第Ⅲ相試験・承認情報

**生成日:** 2026-09-27  
**担当:** QC担当エージェント  
**入力ファイル:** pubmed_gastric.json, pubmed_colorectal.json, pubmed_breast.json, fda.json, pmda.json

---

## 1. 照合件数（がん種別）

| がん種 | PubMed収集 | FDA承認 | PMDA承認 | 合計入力 |
|--------|------------|---------|----------|----------|
| 胃がん（GEA含む） | 7 | 1 | 2 | 10 |
| 大腸がん | 4 | 0（CRC新規承認なし） | 0（要確認1件） | 4 |
| 乳がん | 6 | 9 | 3 | 18 |
| **合計** | **17** | **10** | **5** | **32** |

- FDA承認10件のうち乳がん9件、胃がん1件（大腸がんは期間内新規承認なし）
- PMDA承認5件のうち乳がん3件、胃がん2件（大腸がんは承認日未確認1件）
- 入力合計32件は重複あり（同一試験が複数ファイルに登録）。重複統合後の実エントリ数は下表参照。

---

## 2. 重複発見・統合件数

**統合件数: 3件**

| 試験名 | 重複ソース | 統合内容 |
|--------|------------|----------|
| HERIZON-GEA-01（NCT05152147） | pubmed_gastric.json + fda.json | FDA承認情報（zanidatamab+tislelizumab、2026-08-25）をregulatory.FDAに統合。元pubmed_gastricのregulatory.FDA「Priority Review 付与」を「承認（2026-08-25）」に更新。 |
| MATTERHORN（NCT04592913） | pubmed_gastric.json + pmda.json | PMDA承認情報（durvalumab/イミフィンジ、2026-06-19）をregulatory.PMDAに統合。元pubmed_gastricのregulatory.PMDA「NR」を更新。 |
| TROPION-Breast02（NCT05374512） | pubmed_breast.json + fda.json + pmda.json | FDA承認（Dato-DXd/Datroway、2026-05-22）とPMDA承認（ダトロウェイ、2026-09-16）をregulatory fieldsに統合。 |

---

## 3. 修正件数と内容

**修正件数: 4件**

| 項目 | 修正前 | 修正後 | 理由 |
|------|--------|--------|------|
| HERIZON-GEA-01 regulatory.FDA | "Priority Review 付与（2026年初）" | "承認（zanidatamab-hrii+tislelizumab-jsgr; 2026-08-25）" | fda.jsonの正確な承認情報で上書き |
| MATTERHORN regulatory.PMDA | "NR" | "承認（イミフィンジ/durvalumab; 2026-06-19）" | pmda.jsonの承認情報を追加 |
| MATTERHORN regulatory.FDA | "承認（durvalumab+FLOT、2026年）" | "QC注記: pubmed_gastric.jsonでは承認記録あるがfda.json非収録。要確認フラグ付与" | fda.jsonに対応する承認記録なし。pubmed_gastric担当エージェントの記録と不一致のためフラグ付与（承認時期が2026年5–9月対象期間外の可能性あり） |
| SERENA-6 分類変更 | pubmed_breast.jsonで「E3除外（内分泌療法のみ）」 | 本編trials arrayに収録 | FDA加速承認（2026-09-04）およびPMDA承認（2026-07-10）の直接根拠試験のためQC手順5の例外（FDA/PMDA承認根拠試験）を適用。Lancet Oncol 2026-07-13掲載確認。 |

---

## 4. 除外件数と主な理由

**excluded array: 5件**

| 試験名 | 除外コード | 主な理由 |
|--------|------------|----------|
| KRYSTAL-10 | E_conference_only | ESMO GI 2026学会発表のみ（LBA1）、査読誌未掲載。かつFDA加速承認が2026-09-01に取り消し（KRAS G12C mCRC、主要評価項目PFS・OS共に未達成）。陰性試験として記録。 |
| CLARITY-Gastric01 | E_press_release_only | AstraZenecaプレスリリース（2026-07-27）のみ。詳細数値未開示、査読誌掲載未確認。 |
| ATTRACTION-6 | E_abstract_only | ASCO 2026 Abstract 4006のみ。査読誌未掲載。陰性試験（OS未達成）。 |
| PANKU-Breast02（BL-B01D1-307） | E_abstract_only | ASCO 2026 Abstract LBA1003のみ。査読論文PMID未確認。 |
| KEYNOTE-522（最終OS解析） | E_abstract_only | ASCO 2026 Abstract（JCO suppl）のみ。独立査読論文PMID未確認。OS HR・p値は元データから取得不可のためNR。 |

**事前E5除外（各PubMedファイルで既に除外済み）: 代表的なもの**

| 試験名 | 除外コード | 公表時期 |
|--------|------------|----------|
| PRODIGE 51 GASTFOX | E5 | 2025年4月（Lancet Oncol） |
| DESTINY-Gastric04 | E5 | 2025年（ASCO/NEJM） |
| KEYNOTE-585最終解析 | E5 | 2025年10月（JCO） |
| ATOMIC（atezolizumab大腸）| E5 | 2026年3月（NEJM） |
| ASCENT-03（TNBC）| E5 | 2025年10月（NEJM） |
| ASCENT-04/KEYNOTE-D19 | E5 | 2026年1月（NEJM） |
| DESTINY-Breast05 | E5 | 2025年12月〜2026年2月（NEJM） |
| monarchE OS主要解析 | E5 | 2026年2月（Ann Oncol） |
| culmerciclib（中国） | E5 | 2025年12月 |
| Palbociclib HER2+乳がん | E5 | 2026年1月（NEJM） |

---

## 5. 要確認リスト件数と理由

**review_required array: 1件**

| 試験名 | 要確認理由 | 推奨アクション |
|--------|------------|----------------|
| HORIZON-CRC01 | ASCO 2026会議抄録のみ（JCO 44:16_suppl:3505）。査読論文未掲載。FDA/PMDA承認なし。 | 査読論文掲載（PMID取得）確認後、本編trials arrayに移動して収録。現時点では範囲外。 |

**注: 以下はQC手順5で要確認候補として挙げられたが、例外規定を適用して本編または regulatory_only に振り分け済み。**

| 試験名 | 判断 | 根拠 |
|--------|------|------|
| TROPION-Breast02 | 本編収録（例外適用） | PMID確認済み（41937088、Ann Oncol印刷版2026-08）かつFDA承認（2026-05-22）・PMDA承認（2026-09-16）の根拠試験。epub日問題はflagsに記録。 |
| SERENA-6 | 本編収録（例外適用） | FDA加速承認（2026-09-04）・PMDA承認（2026-07-10）の直接根拠試験、Lancet Oncol 2026-07-13掲載。E3除外（内分泌療法のみ）だが承認根拠として本編収録。 |

---

## 6. 最終エントリ数サマリー

| カテゴリ | 件数 | 内訳 |
|----------|------|------|
| **trials（本編）** | **12** | 胃がん5、大腸がん2、乳がん5 |
| **regulatory_only** | **9** | 乳がん6（DESTINY-Breast05, ASCENT-03, ASCENT-04, PATINA, VERITAC-2, VIKTORIA-1, DESTINY-Breast11）、胃がん1（RATIONALE-305）、乳がん追加1（DESTINY-Breast09 PMDA） |
| **review_required** | **1** | HORIZON-CRC01 |
| **excluded** | **5** | KRYSTAL-10, CLARITY-Gastric01, ATTRACTION-6, PANKU-Breast02, KEYNOTE-522最終解析 |

---

## 7. 数値整合性チェック結果

- **TROPION-Breast02**: pubmed_breast.jsonとfda.json・pmda.jsonで同一試験（NCT05374512）を確認。efficacy数値はpubmed_breast.jsonのデータを採用（fda.jsonにはefficacy数値なし）。矛盾なし。
- **HERIZON-GEA-01**: pubmed_gastric.jsonのNCT05152147とfda.jsonのNCT05152147が一致。efficacy数値は pubmed_gastric.json由来。矛盾なし。
- **MATTERHORN**: pubmed_gastric.json（Lancet Sep 2026 OS解析）とpmda.json（EFS主要解析に基づく承認、NEJM 2025）は別解析・別出版であり矛盾なし。regulatory.FDA（pubmed_gastric.json記載と fda.json非収録）の不一致はフラグとして記録。
- **CheckMate 649**: DOIが「10.1016/j.annonc.2026.01.006」と記録されているが、同一DOIがKC-WISEにも記録されており、どちらかのDOIが不正確な可能性がある。元ファイルの記録を維持しフラグを付与しない（推測による修正は禁止）。

---

## 8. 制限事項

1. **ネットワークアクセス制限**: PubMed（pubmed.ncbi.nlm.nih.gov）、PMC、FDA公式サイト、ESMO/ASCO公式サイト、主要ジャーナル（NEJM、Lancet、Nature、Sciencedirect等）、製薬企業プレスリリースサイト（AstraZeneca等）への直接アクセスが収集時に遮断された。すべての数値はWebSearch経由の二次情報源から取得されており、原著論文・FDA Drugs@FDA・PMDA審議結果報告書の直接検証は未実施。

2. **PMID未確認項目**: HERIZON-GEA-01（NEJM 2026-05-27）、MATTERHORN最終OS（Lancet 2026-09-09）、NSABP B-59（Nature Medicine 2026-09-01）、SERENA-6（Lancet Oncol 2026-07-13）のPMIDが未取得。DOI・URL情報で代替。

3. **PMDA情報源の信頼性**: pmda.json収録の承認日はPMDA公式PDFへのアクセス遮断のため、プレスリリース・医療ニュースサイト・PMDA文書URL中の日付文字列からの推定が含まれる。特にcamizestrant承認日（2026-07-10）はPMDA文書URL「P20260710002」の数字列から推定。

4. **ESMO 2026 Annual Meeting（2026年9月）**: ESMO年次大会（2026年9月）の乳がん第III相試験について、検索予算の制約で完全な捕捉が保証されていない（pubmed_breast.json記載）。本レポートの対象期間（〜2026-09-30）内に追加の重要試験が存在する可能性を排除できない。

5. **encorafenib PMDA大腸がん**: pmda.jsonで「ビラフトビの結腸直腸がん1次治療の効能追加が第二部会で了承」と報告されているが、承認日確認不可（ミクスOnlineへのアクセス遮断）。BREAKWATERコホート3のregulatory.PMDAにQC注記として記録済み。

6. **MATTERHORN FDA承認状況の不一致**: pubmed_gastric.json（収集エージェント作成）には「FDA承認（durvalumab+FLOT、2026年）」と記録されているが、fda.json（FDA担当収集エージェント作成）に同承認の記録がない。FDA承認の有無・時期を公式ソースで要確認。

---

**出力ファイル:**  
- `/home/user/-/work/master.json`  
- `/home/user/-/work/qc_report.md`
