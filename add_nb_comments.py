"""Insert brief inline comments into notebook code cells."""
import json
from copy import deepcopy

NOTEBOOKS = ["50091136.ipynb"]

# cell_index -> list of (substring_match, comment_line)
# comment inserted immediately before the first line containing substring
CELL_INSERTS: dict[int, list[tuple[str, str]]] = {
    43: [
        ("with open(DATA_PATH", "# UTF-8 byte check\n"),
        ("def non_ascii_ratio", "# non-ASCII share helper\n"),
        ("for col in [\"Name\"", "# storefront text scan\n"),
        ("def parse_language_cell", "# parse language list cell\n"),
        ("lang_counter = Counter()", "# top language tokens\n"),
    ],
    46: [
        ("miss_tbl = missingness_summary", "# missingness table\n"),
        ("dup_appid =", "# duplicate key check\n"),
        ("replacement_rows", "# U+FFFD replacement scan\n"),
        ("parseable_share = []", "# numeric-coercible strings\n"),
    ],
    51: [
        ("def owner_band_midpoint", "# owner range midpoint\n"),
        ("mine = pd.DataFrame", "# mining frame\n"),
        ("vote_total =", "# player vote ratio\n"),
        ("corr_mat = mine", "# Pearson correlation\n"),
        ("sns.heatmap", "# correlation heatmap\n"),
    ],
    55: [
        ("plot_df = mine", "# log1p engagement pair\n"),
        ("pear_r, pear_p =", "# raw-scale correlation\n"),
        ("sns.scatterplot", "# subsampled scatter\n"),
    ],
    59: [
        ("meta_block = mine.loc", "# critic + crowd subset\n"),
        ("meta_r, meta_p =", "# Pearson on subset\n"),
        ("sns.regplot", "# regression scatter\n"),
    ],
    63: [
        ("def primary_genre_token", "# first genre token\n"),
        ("df_genre = df.copy()", "# genre price stats\n"),
        ("genre_plot = genre_stats", "# exclude F2P from chart\n"),
        ("sns.barplot", "# median price bars\n"),
    ],
    72: [
        ("shape_before = df.shape", "# before column drop\n"),
        ("df_prep = df.drop", "# slim working table\n"),
    ],
    76: [
        ("work = df_prep.copy()", "# mutable copy\n"),
        ("all_taxonomy_na =", "# hollow-row flag\n"),
        ("work = work.loc[~bad_row]", "# drop hollow rows\n"),
        ("OWNER_PATTERN =", "# owner regex\n"),
        ("parsed = work", "# parse owner bounds\n"),
        ("HIGH_NA_COLS =", "# has_* indicators\n"),
        ("FORBID_FILL =", "# no fill on telemetry\n"),
        ("df_foundation = dataframe_checkpoint", "# checkpoint save\n"),
    ],
    81: [
        ("audit_rows = []", "# IQR / z-score loop\n"),
        ("iqr = q3 - q1", "# Tukey fences\n"),
        ("audit_df = pd.DataFrame", "# sorted audit table\n"),
    ],
    86: [
        ("work = df_foundation.copy()", "# add log1p columns\n"),
        ("work[log_col] = np.log1p", "# parallel log transform\n"),
        ("df_foundation = dataframe_checkpoint", "# refresh checkpoint\n"),
    ],
    91: [
        ("work = df_foundation.copy()", "# sanity pass copy\n"),
        ("drop_row =", "# row drop mask\n"),
        ("work = work.loc[~drop_row]", "# apply row drops\n"),
        ("work.loc[fix_discount", "# fix discount inconsistency\n"),
        ("work.loc[fix_age", "# fix invalid age codes\n"),
    ],
    96: [
        ("miss_before = missingness_summary", "# NA before fill\n"),
        ("work = df_foundation.copy()", "# fill pass copy\n"),
        ("for col in TEXT_FILL_UNKNOWN", "# text -> Unknown\n"),
        ("numeric_targets =", "# sparse numeric only\n"),
        ("miss_after = missingness_summary", "# NA after fill\n"),
    ],
    101: [
        ("BINARY_COLS = [c for c in", "# has_* + platform flags\n"),
        ("issues = []", "# encoding issue list\n"),
        ("for col in MULTI_LABEL_TEXT", "# multi-label text check\n"),
    ],
    110: [
        ("df_model = df_foundation.copy()", "# modelling frame\n"),
        ('df_model["is_active"]', "# binary target\n"),
        ("overlap = [c for c in", "# leakage guard\n"),
        ("X = df_model[FEATURE_COLS]", "# prior feature matrix\n"),
        ("X_train, X_test", "# stratified split\n"),
    ],
    28: [
        ("q_tbl = df[BOX_FEATURES]", "# quartile table\n"),
        ('box_long = df[BOX_FEATURES].melt', "# long format for seaborn\n"),
        ("sns.boxplot(data=box_long", "# raw-scale boxplots\n"),
    ],
    31: [
        ('box_long["log_value"] = np.log1p', "# log1p transform\n"),
        ("sns.boxplot(", "# log-scale boxplots\n"),
    ],
    34: [
        ('pos = df["Positive"]', "# vote count series\n"),
        ("sns.histplot(pos", "# distribution + KDE\n"),
    ],
    37: [
        ('ccu = df["Peak CCU"]', "# concurrency series\n"),
        ("sns.histplot(ccu", "# distribution + KDE\n"),
    ],
    40: [
        ('price = df["Price"]', "# list price series\n"),
        ("sns.histplot(price", "# distribution + KDE\n"),
    ],
    115: [
        ("dt_model = DecisionTreeClassifier", "# shallow tree\n"),
        ("dt_model.fit", "# train on priors\n"),
        ("y_pred = dt_model.predict", "# hold-out predict\n"),
    ],
    120: [
        ("importance = (", "# Gini importances\n"),
        ("importance.plot", "# horizontal bar chart\n"),
    ],
    125: [
        ("fig, ax = plt.subplots", "# tree diagram\n"),
        ("plot_tree(", "# top 3 levels only\n"),
    ],
    134: [
        ("tree = dt_model.tree_", "# sklearn tree struct\n"),
        ("def _collect_leaf_rules", "# DFS leaf walker\n"),
        ("leaf_rules = []", "# collect + sort rules\n"),
    ],
    135: [
        ("TOP_PLOT = 12", "# top leaves to plot\n"),
        ("plot_rules = (", "# sort for barh\n"),
        ("ax.barh(", "# purity bars\n"),
    ],
    140: [
        ("_, _, _, _, idx_train, idx_test =", "# same split indices\n"),
        ('audit = df_model.loc[idx_test]', "# hold-out audit frame\n"),
        ("mis = audit.loc", "# misclassified rows\n"),
        ("fp = mis.loc", "# false positives\n"),
        ("fn = mis.loc", "# false negatives\n"),
        ("def _tag_tokens", "# split tag string\n"),
        ("fp_tags_df = pd.DataFrame", "# for figure cells\n"),
    ],
    141: [
        ("outcome_counts = pd.Series", "# correct / FP / FN counts\n"),
        ("bars = ax.bar", "# outcome bar chart\n"),
    ],
    142: [
        ("fig, axes = plt.subplots", "# FP vs FN tag bars\n"),
        ("for ax, df_tags, title, color in", "# side-by-side panels\n"),
    ],
    151: [
        ("tags_clean = (", "# clean Tags text\n"),
        ("nonempty_mask =", "# non-empty tag rows\n"),
        ("tfidf_vectorizer = TfidfVectorizer", "# 100-term vocabulary\n"),
        ("tfidf_vectorizer.fit", "# fit on non-empty only\n"),
        ("df_tfidf = pd.DataFrame", "# dense TF-IDF table\n"),
    ],
    156: [
        ("K_RANGE = range(2, 9)", "# elbow sweep\n"),
        ("for k in K_RANGE:", "# WCSS per K\n"),
        ("OPT_K = 5", "# operating K\n"),
        ("ax.plot(list(K_RANGE)", "# elbow curve\n"),
    ],
    161: [
        ("kmeans_tags = KMeans", "# final K-Means fit\n"),
        ("df_cluster = df_foundation.copy()", "# labels on foundation\n"),
        ("top_token_rows = []", "# mean TF-IDF tokens\n"),
        ("diag = (", "# cluster diagnostics\n"),
        ("X_ch4 = df_cluster", "# rebuild §4.4 split\n"),
        ("dt_model_ch4 = DecisionTreeClassifier", "# FP/FN bridge tree\n"),
        ("fp_indices = audit_ch4.loc", "# FP row indices\n"),
        ("fn_indices = audit_ch4.loc", "# FN row indices\n"),
        ("diag_display = diag[", "# printable table\n"),
    ],
    162: [
        ("plot_diag = diag_display", "# sorted for plots\n"),
        ("ax.bar(", "# cluster size bars\n"),
    ],
    163: [
        ("activity_colors = plot_diag", "# red/green by activity\n"),
        ("ax.bar(", "# mean is_active bars\n"),
    ],
    164: [
        ("x = np.arange", "# grouped bar positions\n"),
        ("ax.bar(", "# FP / FN share bars\n"),
    ],
    173: [
        ('if "df_foundation" not in globals()', "# prerequisite check\n"),
        ("df_multimodal = df_foundation.copy()", "# multimodal frame\n"),
        ('if "Cluster_ID" not in', "# attach cluster labels\n"),
        ('df_multimodal["release_dt"]', "# parse release date\n"),
        ("cluster_dummies = pd.get_dummies", "# one-hot clusters\n"),
        ("X_fusion = pd.concat", "# numeric + cluster dummies\n"),
        ("is_history = df_multimodal", "# pre-2026 train mask\n"),
        ("is_2026_test = df_multimodal", "# 2026 external test mask\n"),
    ],
    178: [
        ("_REQUIRED_62 = [", "# kernel dependency check\n"),
        ("RF_PARAMS = dict(", "# shared RF hyperparams\n"),
        ("def _classification_metrics", "# metric helper\n"),
        ("model_a = RandomForestClassifier", "# numeric-only model\n"),
        ("model_b = RandomForestClassifier", "# fusion model\n"),
        ("model_a.fit(X_num_hist", "# train A on history\n"),
        ("pred_a_2026 = model_a.predict", "# 2026 predictions\n"),
        ("ablation_df = pd.DataFrame", "# A vs B metrics\n"),
        ("rf_fusion_2026 = model_b", "# save for §6.3\n"),
    ],
    179: [
        ("def _plot_confusion_matrix", "# heatmap helper\n"),
        ("fig, axes = plt.subplots", "# A / B side by side\n"),
        ("cm_a = confusion_matrix", "# print raw counts\n"),
    ],
    184: [
        ("_REQUIRED_63 = [", "# prerequisite check\n"),
        ("df_2026 = df_multimodal.loc", "# 2026 slice\n"),
        ("proba_2026 = rf_fusion_2026", "# survival probability\n"),
        ("trend_2026 = (", "# cluster trend table\n"),
        ("trend_html = trend_2026.to_html", "# HTML display\n"),
    ],
}


def _lines_to_str(lines: list[str]) -> str:
    return "".join(lines)


def _str_to_lines(text: str) -> list[str]:
    if not text:
        return []
    if text.endswith("\n"):
        return [text]
    return [text + "\n"] if "\n" not in text else text.splitlines(keepends=True)


def insert_comments(lines: list[str], inserts: list[tuple[str, str]]) -> list[str]:
    text = _lines_to_str(lines)
    # apply in order; skip if comment already present
    for needle, comment in inserts:
        if comment.strip() in text:
            continue
        pos = text.find(needle)
        if pos == -1:
            continue
        line_start = text.rfind("\n", 0, pos) + 1
        text = text[:line_start] + comment + text[line_start:]
    return _str_to_lines(text)


def patch_notebook(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    n = 0
    for idx, inserts in CELL_INSERTS.items():
        cell = nb["cells"][idx]
        if cell["cell_type"] != "code":
            raise ValueError(f"Cell {idx} not code in {path}")
        new_src = insert_comments(cell.get("source", []), inserts)
        if new_src != cell.get("source", []):
            cell["source"] = new_src
            n += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    return n


if __name__ == "__main__":
    for nb_path in NOTEBOOKS:
        count = patch_notebook(nb_path)
        print(f"{nb_path}: updated {count} cells")
