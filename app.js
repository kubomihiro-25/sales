const companies = [
  { name: "ネクストウェーブ株式会社", people: [{ name: "山田 恒一", role: "情報システム部 部長", deals: ["基幹システム刷新", "定例フォロー 06/12"] }] },
  { name: "グローバルリンク株式会社", people: [{ name: "佐藤 美咲", role: "DX推進室", deals: ["AI活用プロジェクト"] }] },
  { name: "アークテック株式会社", people: [{ name: "鈴木 恒一", role: "開発本部", deals: ["開発体制強化"] }] }
];

const tree = document.querySelector("#knowledgeTree");
const toast = document.querySelector("#toast");
const showToast = (message) => {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2600);
};

function renderTree() {
  tree.innerHTML = companies.map((company, index) => `
    <div class="tree-company">
      <div class="tree-row ${index === 0 ? "selected" : ""}" data-company="${index}"><span class="chevron">⌄</span><span class="node-icon">▣</span>${company.name}</div>
      <div class="tree-child">
        ${company.people.map(person => `<div class="tree-row"><span class="chevron">⌄</span><span class="node-icon">♙</span>${person.name}</div><div class="tree-child">
          <div class="tree-row"><span class="chevron">›</span><span class="node-icon">◈</span>${person.role}</div>
          <div class="tree-child">${person.deals.map((deal, dealIndex) => `<div class="tree-row ${index === 0 && dealIndex === 1 ? "active" : ""}" data-deal="${deal}"><span class="chevron">›</span><span class="node-icon">◷</span>${deal}</div>`).join("")}</div>
        </div>`).join("")}
      </div>
    </div>`).join("");
  tree.querySelectorAll("[data-company]").forEach(row => row.addEventListener("click", () => selectCompany(Number(row.dataset.company))));
  tree.querySelectorAll("[data-deal]").forEach(row => row.addEventListener("click", () => showToast(`「${row.dataset.deal}」を選択しました`)));
}

function selectCompany(index) {
  const company = companies[index];
  document.querySelector("#companyName").textContent = company.name;
  document.querySelector("#currentBreadcrumb").textContent = company.name;
  tree.querySelectorAll("[data-company]").forEach(row => row.classList.toggle("selected", Number(row.dataset.company) === index));
  showToast(`${company.name}のナレッジを表示しました`);
}

renderTree();

document.querySelectorAll(".ai-tab").forEach(tab => tab.addEventListener("click", () => {
  document.querySelectorAll(".ai-tab").forEach(item => item.classList.remove("active"));
  tab.classList.add("active");
  const isScenario = tab.dataset.tab === "scenario";
  document.querySelector("#scenarioPanel").classList.toggle("hidden", !isScenario);
  document.querySelector("#ballPanel").classList.toggle("hidden", isScenario);
}));

const scenarioMarkup = () => `
  <div class="output-title"><h3>商談シナリオ <span class="ai-badge">生成完了</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div>
  <div class="scenario-columns">
    <div><p class="section-label">大枠シナリオ</p><div class="keyword-list"><span class="keyword">課題の再定義</span><span class="keyword">来期計画</span><span class="keyword">刷新ロードマップ</span><span class="keyword">Azure移行</span><span class="keyword">次回提案</span></div><p class="section-label">今回のゴール</p><div class="goal-box">来期のシステム刷新計画と意思決定プロセスを把握し、Azure移行を含む伴走支援の提案機会をつくる。</div></div>
    <div><p class="section-label">進行イメージ</p><div class="outline-item"><span class="outline-num">1</span><div><strong>アイスブレイク・現状確認</strong><p>前回からの変化と、現在感じている課題を確認する。</p></div></div><div class="outline-item"><span class="outline-num">2</span><div><strong>課題と背景の深掘り</strong><p>刷新の背景、優先度、制約条件を質問で引き出す。</p></div></div><div class="outline-item"><span class="outline-num">3</span><div><strong>方向性のすり合わせ</strong><p>支援可能な領域を示し、次回の具体提案へつなげる。</p></div></div><div class="talk-details"><p class="section-label">確認すべき質問例</p><p class="talk-summary">「刷新の成功を、どのような指標で捉えていますか？」「現時点で最もボトルネックになっている工程はどこですか？」</p><div class="agenda"><span>目的・背景</span><span>体制・予算</span><span>スケジュール</span><span>意思決定者</span></div></div></div>
  </div>`;

document.querySelector("#generateScenario").addEventListener("click", async () => {
  const button = document.querySelector("#generateScenario");
  button.disabled = true; button.textContent = "生成中…";
  const result = await callNewtonXADK("scenario", { purpose: document.querySelector("#purpose").value, status: document.querySelector("#status").value, context: document.querySelector("#scenarioInput").value });
  document.querySelector("#scenarioOutput").innerHTML = result || scenarioMarkup();
  document.querySelector("#scenarioOutput").classList.remove("hidden");
  button.disabled = false; button.textContent = "✦ シナリオを生成";
  document.querySelector("[data-save]")?.addEventListener("click", () => showToast("商談履歴に保存しました"));
});

const ballMarkup = () => `
  <div class="output-title"><h3>ボール管理レポート <span class="ai-badge blue-badge">分析完了</span></h3><button class="save-btn" data-save>↓ 履歴に保存</button></div>
  <div class="analysis-grid"><div class="metric"><small>商談フェーズ</small><strong>課題整理・提案前</strong></div><div class="metric"><small>ボール保有者</small><strong class="orange">顧客側（山田様）</strong></div><div class="metric"><small>案件確度</small><strong class="green">60%　↑</strong></div></div>
  <div class="analysis-columns"><div class="analysis-block"><h4>顧客課題・未確認事項</h4><ul class="check-list"><li>既存システムの運用コストが増加</li><li>来期予算と意思決定スケジュール</li><li>移行後の運用体制・内製化方針</li></ul><h4 style="margin-top:22px">注意すべきリスク</h4><ul class="check-list risk"><li>競合ベンダーも同時に比較中</li><li>決裁者との接点がまだない</li></ul></div><div class="analysis-block"><h4>推奨する次回アクション</h4><ul class="check-list"><li>6月末までに刷新ロードマップの叩き台を送付</li><li>決裁者を含む次回提案会を打診</li></ul><h4 style="margin-top:22px">推奨商材・関連資料</h4><div class="product-card"><div class="product-icon">◈</div><div><strong>Azure移行アセスメントサービス</strong><small>サービス紹介資料 ・ 導入事例 2件</small></div></div><div class="product-card"><div class="product-icon">▤</div><div><strong>基幹システム刷新 提案テンプレート</strong><small>提案書 ・ 価格表</small></div></div></div></div>`;

document.querySelector("#analyzeMeeting").addEventListener("click", async () => {
  const button = document.querySelector("#analyzeMeeting");
  button.disabled = true; button.textContent = "分析中…";
  const result = await callNewtonXADK("ball", { transcript: document.querySelector("#meetingInput").value });
  document.querySelector("#ballOutput").innerHTML = result || ballMarkup();
  document.querySelector("#ballOutput").classList.remove("hidden");
  button.disabled = false; button.textContent = "◌ 商談を分析";
  document.querySelector("[data-save]")?.addEventListener("click", () => showToast("商談履歴に保存しました"));
});

async function callNewtonXADK(type, payload) {
  try {
    const response = await fetch(`/api/newtonxadk/${type}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!response.ok) return null;
    const data = await response.json();
    return data.html || null;
  } catch (error) {
    console.warn(`NewtonXADK ${type} endpoint is unavailable; showing demo output.`, error);
    return null;
  }
}

document.querySelector("#libraryBtn").addEventListener("click", () => showToast("商材ライブラリ（24件）を開きました"));
document.querySelector("#addCompany").addEventListener("click", () => showToast("企業追加はNewtonXADKの顧客管理と連携します"));
