const companies = [
  { name: "株式会社アトラス", people: [{ name: "山田 太郎", role: "情報システム部 部長", deals: ["基幹システム刷新", "定例フォロー 06/12"] }] },
  { name: "ネクストソリューションズ", people: [{ name: "佐藤 花子", role: "DX推進室", deals: ["AI活用支援"] }] },
  { name: "グローバルテック", people: [{ name: "鈴木 一郎", role: "開発部", deals: ["人材提案"] }] }
];
const tree = document.querySelector("#knowledgeTree");
const toast = document.querySelector("#toast");
const settings = {
  get url() { return window.location.origin; },
  get model() { return localStorage.getItem("newtonx.aiModel") || "newtonxadk-default"; }
};
const showToast = message => { toast.textContent = message; toast.classList.add("show"); window.setTimeout(() => toast.classList.remove("show"), 2600); };

function renderTree() {
  tree.innerHTML = companies.map((company, index) => `<div class="tree-company"><div class="tree-row ${index === 0 ? "selected" : ""}" data-company="${index}"><span class="chevron">⌄</span><span class="node-icon">▣</span>${company.name}</div><div class="tree-child">${company.people.map(person => `<div class="tree-row"><span class="chevron">⌄</span><span class="node-icon">♙</span>${person.name}</div><div class="tree-child"><div class="tree-row"><span class="chevron">⌄</span><span class="node-icon">◆</span>${person.role}</div><div class="tree-child">${person.deals.map((deal, dealIndex) => `<div class="tree-row ${index === 0 && dealIndex === 1 ? "active" : ""}" data-deal="${deal}"><span class="chevron">•</span><span class="node-icon">▤</span>${deal}</div>`).join("")}</div></div>`).join("")}</div></div>`).join("");
  tree.querySelectorAll("[data-company]").forEach(row => row.addEventListener("click", () => selectCompany(Number(row.dataset.company))));
  tree.querySelectorAll("[data-deal]").forEach(row => row.addEventListener("click", () => showToast(`${row.dataset.deal}を選択しました`)));
}
function selectCompany(index) {
  const company = companies[index];
  document.querySelector("#companyName").textContent = company.name;
  document.querySelector("#currentBreadcrumb").textContent = company.name;
  tree.querySelectorAll("[data-company]").forEach(row => row.classList.toggle("selected", Number(row.dataset.company) === index));
  showToast(`${company.name}を選択しました`);
}
renderTree();

document.querySelectorAll(".ai-tab").forEach(tab => tab.addEventListener("click", () => {
  document.querySelectorAll(".ai-tab").forEach(item => item.classList.remove("active"));
  tab.classList.add("active");
  const scenario = tab.dataset.tab === "scenario";
  document.querySelector("#scenarioPanel").classList.toggle("hidden", !scenario);
  document.querySelector("#ballPanel").classList.toggle("hidden", scenario);
}));
const scenarioMarkup = () => `<div class="output-title"><h3>商談シナリオ <span class="ai-badge">AI生成</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div><div class="scenario-columns"><div><p class="section-label">キーワード</p><div class="keyword-list"><span class="keyword">課題整理</span><span class="keyword">予算</span><span class="keyword">意思決定</span><span class="keyword">Azure提案</span><span class="keyword">次回提案</span></div><p class="section-label">今回のゴール</p><div class="goal-box">顧客の課題と意思決定プロセスを把握し、次回提案につながる合意を形成する。</div></div><div><p class="section-label">進行イメージ</p><div class="outline-item"><span class="outline-num">1</span><div><strong>現状確認</strong><p>前回からの変化と現在の課題を確認する。</p></div></div><div class="outline-item"><span class="outline-num">2</span><div><strong>課題と背景の深掘り</strong><p>優先度、制約条件、体制を質問で引き出す。</p></div></div><div class="outline-item"><span class="outline-num">3</span><div><strong>次回提案の合意</strong><p>提案内容、参加者、次回日程を決定する。</p></div></div><div class="talk-details"><p class="section-label">質問例</p><p class="talk-summary">「成功をどのような指標で捉えていますか？」「最もボトルネックになっている工程はどこですか？」</p><div class="agenda"><span>目的・背景</span><span>体制・予算</span><span>スケジュール</span><span>意思決定者</span></div></div></div></div>`;
const ballMarkup = () => `<div class="output-title"><h3>ボール管理レポート <span class="ai-badge blue-badge">AI分析</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div><div class="analysis-grid"><div class="metric"><small>商談フェーズ</small><strong>課題整理・提案前</strong></div><div class="metric"><small>ボール保有者</small><strong class="orange">顧客側（山田様）</strong></div><div class="metric"><small>案件確度</small><strong class="green">60% ↑</strong></div></div><div class="analysis-columns"><div class="analysis-block"><h4>顧客課題・未確認事項</h4><ul class="check-list"><li>既存システムの運用コストが増加</li><li>来期予算と意思決定スケジュール</li><li>移行後の運用体制・内製化方針</li></ul><h4 style="margin-top:22px">注意すべきリスク</h4><ul class="check-list risk"><li>競合ベンダーも同時に比較中</li><li>決裁者との接点がまだない</li></ul></div><div class="analysis-block"><h4>推奨する次回アクション</h4><ul class="check-list"><li>刷新ロードマップの叩き台を送付</li><li>決裁者を含む次回提案会を打診</li></ul><h4 style="margin-top:22px">推奨商材・関連資料</h4><div class="product-card"><div class="product-icon">◈</div><div><strong>Azure移行アセスメントサービス</strong><small>サービス紹介資料・導入事例 2件</small></div></div><div class="product-card"><div class="product-icon">▤</div><div><strong>基幹システム刷新 提案テンプレート</strong><small>提案書・価格表</small></div></div></div></div>`;

async function callNewtonXADK(type, payload) {
  try {
    const response = await fetch(`${settings.url}/api/newtonxadk/${type}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.assign({}, payload, { model: settings.model })) });
    if (!response.ok) return null;
    const data = await response.json();
    return data.html || null;
  } catch (error) {
    console.warn(`NewtonXADK ${type} endpoint is unavailable; showing demo output.`, error);
    return null;
  }
}
async function generate(type) {
  const button = document.querySelector(type === "scenario" ? "#generateScenario" : "#analyzeMeeting");
  const output = document.querySelector(type === "scenario" ? "#scenarioOutput" : "#ballOutput");
  button.disabled = true;
  button.textContent = type === "scenario" ? "生成中..." : "分析中...";
  const payload = type === "scenario" ? { purpose: document.querySelector("#purpose").value, status: document.querySelector("#status").value, context: document.querySelector("#scenarioInput").value } : { transcript: document.querySelector("#meetingInput").value };
  output.innerHTML = (await callNewtonXADK(type, payload)) || (type === "scenario" ? scenarioMarkup() : ballMarkup());
  output.classList.remove("hidden");
  button.disabled = false;
  button.textContent = type === "scenario" ? "商談シナリオを生成" : "商談を分析";
  output.querySelector("[data-save]").addEventListener("click", () => showToast("商談履歴に保存しました"));
}
document.querySelector("#generateScenario").addEventListener("click", () => generate("scenario"));
document.querySelector("#analyzeMeeting").addEventListener("click", () => generate("ball"));
document.querySelector("#libraryBtn").addEventListener("click", () => showToast("商材ライブラリ（24件）を開きました"));
document.querySelector("#addCompany").addEventListener("click", () => showToast("顧客情報を追加するにはNewtonXADKへ接続してください"));

function updateConnectionStatus(message, connected) { const status = document.querySelector("#settingsStatus"); status.classList.toggle("connected", connected); status.querySelector("span").textContent = message; }
async function openSettings() {
  document.querySelector("#apiBaseUrl").value = "https://seraku.newton-x.net/api";
  document.querySelector("#accessToken").value = "";
  document.querySelector("#aiModel").value = settings.model;
  document.querySelector("#settingsBackdrop").classList.remove("hidden");
  try {
    const response = await fetch("/api/settings/status");
    const data = await response.json();
    document.querySelector("#apiBaseUrl").value = data.api_base_url || "https://seraku.newton-x.net/api";
    document.querySelector("#aiModel").value = data.default_model || settings.model;
    updateConnectionStatus(data.configured ? `${data.default_model || settings.model} / PAT設定済み` : "PAT未設定", data.configured);
  } catch (error) {
    updateConnectionStatus("接続状態を取得できません", false);
  }
}
document.querySelector("#settingsBtn").addEventListener("click", openSettings);
document.querySelector("#closeSettings").addEventListener("click", () => document.querySelector("#settingsBackdrop").classList.add("hidden"));
document.querySelector("#settingsBackdrop").addEventListener("click", event => { if (event.target.id === "settingsBackdrop") event.currentTarget.classList.add("hidden"); });
document.querySelector("#toggleToken").addEventListener("click", event => { const input = document.querySelector("#accessToken"); input.type = input.type === "password" ? "text" : "password"; event.currentTarget.textContent = input.type === "password" ? "表示" : "隠す"; });
document.querySelector("#saveSettings").addEventListener("click", async () => {
  const url = document.querySelector("#apiBaseUrl").value.trim().replace(/\/$/, "") || window.location.origin;
  const token = document.querySelector("#accessToken").value.trim();
  const model = document.querySelector("#aiModel").value;
  try {
    const response = await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pat: token, model, api_base_url: url }) });
    if (!response.ok) throw new Error(`設定の保存に失敗しました（${response.status}）`);
    localStorage.setItem("newtonx.aiModel", model);
    updateConnectionStatus(`${model} / PAT設定済み`, Boolean(token));
    showToast("NewtonX接続設定を保存しました");
  } catch (error) { updateConnectionStatus("接続エラー", false); showToast(error.message); }
});
document.querySelector("#testConnection").addEventListener("click", async () => {
  const button = document.querySelector("#testConnection");
  button.disabled = true; button.textContent = "確認中...";
  try {
    const response = await fetch("/api/settings/status");
    const data = await response.json();
    updateConnectionStatus(data.configured ? `${data.default_model || settings.model} / 接続済み` : "PAT未設定", data.configured);
  } catch (error) { updateConnectionStatus("接続エラー", false); }
  finally { button.disabled = false; button.textContent = "接続テスト"; }
});
document.querySelector("#loadModels").addEventListener("click", async () => {
  const button = document.querySelector("#loadModels");
  button.disabled = true; button.textContent = "取得中...";
  try {
    const response = await fetch("/api/settings/models");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "モデル一覧を取得できませんでした");
    const select = document.querySelector("#aiModel");
    select.innerHTML = "";
    data.models.forEach(item => { const option = document.createElement("option"); option.value = item.name; option.textContent = item.name; select.appendChild(option); });
    updateConnectionStatus(`${data.models.length}件のモデルを取得しました`, true);
  } catch (error) { updateConnectionStatus("モデル取得エラー", false); showToast(error.message); }
  finally { button.disabled = false; button.textContent = "NewtonXモデル一覧を取得"; }
});
