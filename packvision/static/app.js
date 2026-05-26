const translations = {
  zh: {
    localLab: "本地仓库测量台",
    measure: "测量",
    history: "历史",
    calibration: "校准卡",
    localApi: "本地 API",
    project: "包装尺寸检测",
    title: "手机照片、侧面照和人工修正一起测",
    language: "语言",
    light: "明亮",
    dark: "深色",
    graphite: "石墨",
    guideModeTitle: "多种比例来源",
    guideModeText: "优先用 ArUco；没有标记时可用距离和焦距做估算。",
    guideSideTitle: "侧面照可算高度",
    guideSideText: "顶部取长宽，侧面取高度候选，异形件可手动框选。",
    guideTraceTitle: "单号追溯",
    guideTraceText: "扫码枪、条码图片和手工录入都会保存到历史记录。",
    capture: "采集",
    uploadSet: "上传图片和单号",
    printMarker: "打印标记",
    orderId: "单号",
    barcodeText: "扫码文本",
    decodeBarcode: "识别条码图片",
    decoding: "识别中",
    barcodeFound: "已识别单号",
    barcodeNotFound: "未识别到条码",
    topPhoto: "顶部照片",
    sidePhoto: "侧面照片",
    noFile: "未选择文件",
    optional: "可选",
    measurementMode: "测量参数",
    estimateNote: "无卡模式需要距离和焦距，结果为估算。",
    markerSize: "标记边长，毫米",
    manualHeight: "人工高度，毫米",
    cameraDistance: "相机距离，毫米",
    focal35: "等效焦距，毫米",
    runMeasure: "开始测量",
    measuring: "测量中",
    loadDemo: "加载演示图",
    result: "结果",
    waiting: "等待图片",
    measured: "已完成测量",
    needsReference: "需要参考或修正",
    length: "长",
    width: "宽",
    height: "高",
    volume: "体积",
    emptyStage: "上传顶部照片后开始",
    drawHint: "拖拽框选需要修正的范围",
    adjustBox: "手动修正框",
    topView: "顶部",
    sideView: "侧面",
    api: "API",
    confidence: "置信度",
    error: "测量失败",
    copyJson: "复制 JSON",
    copied: "已复制",
    openImage: "打开标注图",
    historyTitle: "带时间戳的测量记录",
    refresh: "刷新",
    noHistory: "还没有匹配的历史记录",
    manualBoxReady: "手动框已应用",
    sideSummary: "侧面高度候选",
  },
  en: {
    localLab: "Local warehouse station",
    measure: "Measure",
    history: "History",
    calibration: "Calibration",
    localApi: "Local API",
    project: "Packaging dimension detection",
    title: "Measure with phone photos, side views, and manual correction",
    language: "Language",
    light: "Light",
    dark: "Dark",
    graphite: "Graphite",
    guideModeTitle: "Multiple scale sources",
    guideModeText: "Use ArUco first; estimate from distance and focal length when no marker is available.",
    guideSideTitle: "Side photos estimate height",
    guideSideText: "Top view gives length and width; side view gives a height candidate.",
    guideTraceTitle: "Order traceability",
    guideTraceText: "Scanner input, barcode images, and manual entry are saved to history.",
    capture: "Capture",
    uploadSet: "Upload photos and order",
    printMarker: "Print marker",
    orderId: "Order ID",
    barcodeText: "Scanned text",
    decodeBarcode: "Decode barcode image",
    decoding: "Decoding",
    barcodeFound: "Order detected",
    barcodeNotFound: "No barcode detected",
    topPhoto: "Top photo",
    sidePhoto: "Side photo",
    noFile: "No file selected",
    optional: "Optional",
    measurementMode: "Measurement parameters",
    estimateNote: "No-card mode needs distance and focal length; results are estimates.",
    markerSize: "Marker size, mm",
    manualHeight: "Manual height, mm",
    cameraDistance: "Camera distance, mm",
    focal35: "35mm equiv. focal, mm",
    runMeasure: "Measure package",
    measuring: "Measuring",
    loadDemo: "Load demo image",
    result: "Result",
    waiting: "Waiting for image",
    measured: "Measured",
    needsReference: "Reference or correction needed",
    length: "Length",
    width: "Width",
    height: "Height",
    volume: "Volume",
    emptyStage: "Upload a top photo to begin",
    drawHint: "Drag to correct the detected range",
    adjustBox: "Manual box",
    topView: "Top",
    sideView: "Side",
    api: "API",
    confidence: "Confidence",
    error: "Measurement failed",
    copyJson: "Copy JSON",
    copied: "Copied",
    openImage: "Open image",
    historyTitle: "Timestamped measurement records",
    refresh: "Refresh",
    noHistory: "No matching history yet",
    manualBoxReady: "Manual box applied",
    sideSummary: "Side height candidate",
  },
  uk: {
    localLab: "Локальна станція складу",
    measure: "Вимір",
    history: "Історія",
    calibration: "Калібрування",
    localApi: "Локальний API",
    project: "Вимірювання пакування",
    title: "Фото з телефона, бічний вигляд і ручна корекція",
    language: "Мова",
    light: "Світла",
    dark: "Темна",
    graphite: "Графіт",
    guideModeTitle: "Кілька джерел масштабу",
    guideModeText: "Спершу ArUco; без маркера можна оцінити за відстанню та фокусом.",
    guideSideTitle: "Бічне фото дає висоту",
    guideSideText: "Верхній вигляд дає довжину і ширину, бічний - кандидат висоти.",
    guideTraceTitle: "Відстеження замовлень",
    guideTraceText: "Сканер, фото штрихкоду і ручний ввід зберігаються в історії.",
    capture: "Збір",
    uploadSet: "Фото та номер",
    printMarker: "Друк маркера",
    orderId: "Номер",
    barcodeText: "Текст скану",
    decodeBarcode: "Зчитати штрихкод",
    decoding: "Зчитування",
    barcodeFound: "Номер знайдено",
    barcodeNotFound: "Штрихкод не знайдено",
    topPhoto: "Фото зверху",
    sidePhoto: "Фото збоку",
    noFile: "Файл не вибрано",
    optional: "Необов'язково",
    measurementMode: "Параметри",
    estimateNote: "Без картки потрібні відстань і фокус; це оцінка.",
    markerSize: "Розмір маркера, мм",
    manualHeight: "Висота вручну, мм",
    cameraDistance: "Відстань камери, мм",
    focal35: "Фокус 35 мм, мм",
    runMeasure: "Виміряти",
    measuring: "Вимірювання",
    loadDemo: "Завантажити демо",
    result: "Результат",
    waiting: "Очікування фото",
    measured: "Виміряно",
    needsReference: "Потрібна опора або корекція",
    length: "Довжина",
    width: "Ширина",
    height: "Висота",
    volume: "Об'єм",
    emptyStage: "Додайте фото зверху",
    drawHint: "Перетягніть, щоб виправити область",
    adjustBox: "Ручна рамка",
    topView: "Верх",
    sideView: "Бік",
    api: "API",
    confidence: "Довіра",
    error: "Помилка вимірювання",
    copyJson: "Копіювати JSON",
    copied: "Скопійовано",
    openImage: "Відкрити фото",
    historyTitle: "Історія з часовими мітками",
    refresh: "Оновити",
    noHistory: "Записів ще немає",
    manualBoxReady: "Рамку застосовано",
    sideSummary: "Кандидат висоти збоку",
  },
};

const flagLabels = {
  zh: {
    aruco_marker_scale_used: "使用 ArUco 标记比例",
    aruco_reference_detected: "已识别参考标记",
    camera_distance_exif_scale_used: "使用照片 EXIF 估算比例",
    camera_distance_manual_focal_scale_used: "使用距离和焦距估算比例",
    height_missing: "缺少高度",
    manual_annotation_used: "使用手动标注",
    manual_height_used: "使用人工高度",
    manual_side_box_used: "侧面手动框",
    manual_top_box_used: "顶部手动框",
    missing_aruco_reference: "未识别 ArUco 标记",
    package_contour_not_found: "未找到包装轮廓",
    package_small_in_frame: "包装在画面中偏小",
    side_aruco_marker_scale_used: "侧面使用 ArUco 比例",
    side_aruco_reference_detected: "侧面标记已识别",
    side_camera_distance_exif_scale_used: "侧面使用 EXIF 估算",
    side_camera_distance_manual_focal_scale_used: "侧面使用距离和焦距估算",
    side_view_height_estimated: "使用侧面图估算高度",
    single_camera_perspective_limited: "单目照片存在透视限制",
  },
  en: {
    aruco_marker_scale_used: "ArUco scale used",
    aruco_reference_detected: "Reference marker detected",
    camera_distance_exif_scale_used: "EXIF distance scale used",
    camera_distance_manual_focal_scale_used: "Distance and focal estimate used",
    height_missing: "Height missing",
    manual_annotation_used: "Manual annotation used",
    manual_height_used: "Manual height used",
    manual_side_box_used: "Manual side box",
    manual_top_box_used: "Manual top box",
    missing_aruco_reference: "ArUco marker missing",
    package_contour_not_found: "Package contour not found",
    package_small_in_frame: "Package is small in frame",
    side_aruco_marker_scale_used: "Side ArUco scale used",
    side_aruco_reference_detected: "Side marker detected",
    side_camera_distance_exif_scale_used: "Side EXIF estimate used",
    side_camera_distance_manual_focal_scale_used: "Side distance estimate used",
    side_view_height_estimated: "Height estimated from side view",
    single_camera_perspective_limited: "Single-camera perspective limit",
  },
  uk: {
    aruco_marker_scale_used: "Масштаб ArUco",
    aruco_reference_detected: "Маркер знайдено",
    camera_distance_exif_scale_used: "Масштаб з EXIF",
    camera_distance_manual_focal_scale_used: "Оцінка за відстанню",
    height_missing: "Висота відсутня",
    manual_annotation_used: "Ручна розмітка",
    manual_height_used: "Ручна висота",
    manual_side_box_used: "Ручна рамка збоку",
    manual_top_box_used: "Ручна рамка зверху",
    missing_aruco_reference: "Немає маркера ArUco",
    package_contour_not_found: "Контур не знайдено",
    package_small_in_frame: "Об'єкт малий у кадрі",
    side_aruco_marker_scale_used: "Бічний масштаб ArUco",
    side_aruco_reference_detected: "Бічний маркер знайдено",
    side_camera_distance_exif_scale_used: "Бічна оцінка EXIF",
    side_camera_distance_manual_focal_scale_used: "Бічна оцінка відстані",
    side_view_height_estimated: "Висота з бічного фото",
    single_camera_perspective_limited: "Обмеження однієї камери",
  },
};

const recommendationLabels = {
  zh: {
    add_height_or_side_photo: "补充侧面照片，或在人工高度中输入真实高度。",
    distance_mode_is_estimate: "无卡估算会受拍摄距离、焦距和透视影响，建议抽检复核。",
    keep_camera_top_down: "顶部照尽量垂直拍摄，减少透视带来的长宽误差。",
    move_camera_closer: "包装占画面比例偏小，建议靠近一点重新拍摄。",
    place_or_print_marker: "要高精度，请打印校准卡并把标记放在包装同一平面。",
    retake_on_plain_background: "换成更干净的背景，并保证边缘清晰。",
    use_distance_mode_or_marker: "没有标记时，可以输入相机距离和等效焦距进行估算。",
  },
  en: {
    add_height_or_side_photo: "Add a side photo or type the real height manually.",
    distance_mode_is_estimate: "No-card mode is affected by distance, focal length, and perspective; spot-check it.",
    keep_camera_top_down: "Use a top-down angle to reduce perspective error.",
    move_camera_closer: "The parcel is small in frame; retake closer if possible.",
    place_or_print_marker: "For higher precision, print the calibration card and place it on the same plane.",
    retake_on_plain_background: "Use a cleaner background with clearer parcel edges.",
    use_distance_mode_or_marker: "Without a marker, enter camera distance and 35mm focal length for estimation.",
  },
  uk: {
    add_height_or_side_photo: "Додайте бічне фото або введіть реальну висоту.",
    distance_mode_is_estimate: "Режим без картки залежить від відстані, фокуса і перспективи.",
    keep_camera_top_down: "Знімайте зверху, щоб зменшити похибку перспективи.",
    move_camera_closer: "Об'єкт малий у кадрі; зніміть ближче.",
    place_or_print_marker: "Для точності надрукуйте картку калібрування.",
    retake_on_plain_background: "Використайте чистіший фон і чіткі краї.",
    use_distance_mode_or_marker: "Без маркера введіть відстань камери та фокус 35 мм.",
  },
};

const localeMap = { zh: "zh-CN", en: "en-US", uk: "uk-UA" };

const state = {
  lang: localStorage.getItem("packvision.lang") || "zh",
  theme: localStorage.getItem("packvision.theme") || "light",
  lastResult: null,
  activeView: "top",
  previewUrls: { top: null, side: null },
  drawing: { active: false, start: null, current: null },
};

const form = document.querySelector("#measureForm");
const languageSelect = document.querySelector("#languageSelect");
const topImage = document.querySelector("#topImage");
const sideImage = document.querySelector("#sideImage");
const topFileName = document.querySelector("#topFileName");
const sideFileName = document.querySelector("#sideFileName");
const topPreview = document.querySelector("#topPreview");
const sidePreview = document.querySelector("#sidePreview");
const measureButton = document.querySelector("#measureButton");
const demoButton = document.querySelector("#demoButton");
const orderIdInput = document.querySelector("#orderId");
const barcodeTextInput = document.querySelector("#barcodeText");
const orderImage = document.querySelector("#orderImage");
const decodeBarcodeButton = document.querySelector("#decodeBarcodeButton");
const topBoxJson = document.querySelector("#topBoxJson");
const sideBoxJson = document.querySelector("#sideBoxJson");
const resultTitle = document.querySelector("#resultTitle");
const confidenceValue = document.querySelector("#confidenceValue");
const annotatedImage = document.querySelector("#annotatedImage");
const imageStage = document.querySelector("#imageStage");
const annotationCanvas = document.querySelector("#annotationCanvas");
const drawHint = document.querySelector("#drawHint");
const emptyStage = document.querySelector("#emptyStage");
const qualityFlags = document.querySelector("#qualityFlags");
const recommendations = document.querySelector("#recommendations");
const copyJsonButton = document.querySelector("#copyJsonButton");
const openImageLink = document.querySelector("#openImageLink");
const adjustTopButton = document.querySelector("#adjustTopButton");
const showTopViewButton = document.querySelector("#showTopViewButton");
const showSideViewButton = document.querySelector("#showSideViewButton");
const sideSummary = document.querySelector("#sideSummary");
const historySearch = document.querySelector("#historySearch");
const historyList = document.querySelector("#historyList");
const refreshHistoryButton = document.querySelector("#refreshHistoryButton");

const metricEls = {
  length_mm: document.querySelector("#lengthValue"),
  width_mm: document.querySelector("#widthValue"),
  height_mm: document.querySelector("#heightValue"),
  volume_l: document.querySelector("#volumeValue"),
};

function t(key) {
  return translations[state.lang]?.[key] || translations.en[key] || key;
}

function labelFrom(dictionary, key) {
  return dictionary[state.lang]?.[key] || dictionary.en[key] || key.replaceAll("_", " ");
}

function applyLanguage() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : state.lang;
  languageSelect.value = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  localStorage.setItem("packvision.lang", state.lang);
  setFileName(topImage, topFileName, "noFile");
  setFileName(sideImage, sideFileName, "optional");
  if (state.lastResult) {
    renderResult(state.lastResult, { keepView: true });
  } else {
    loadHistory();
  }
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  document.querySelectorAll("[data-theme-choice]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.themeChoice === state.theme);
  });
  localStorage.setItem("packvision.theme", state.theme);
}

function formatMm(value) {
  return Number.isFinite(Number(value)) ? `${Number(value).toFixed(1)} mm` : "--";
}

function formatVolume(value) {
  return Number.isFinite(Number(value)) ? `${Number(value).toFixed(3)} L` : "--";
}

function formatDate(value) {
  if (!value) {
    return "--";
  }
  return new Date(value).toLocaleString(localeMap[state.lang], {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function setFileName(input, target, fallbackKey) {
  target.textContent = input.files?.[0]?.name || t(fallbackKey);
}

function setBusy(isBusy) {
  measureButton.disabled = isBusy;
  demoButton.disabled = isBusy;
  measureButton.querySelector("span").textContent = isBusy ? t("measuring") : t("runMeasure");
}

function setInputFile(input, file) {
  const transfer = new DataTransfer();
  transfer.items.add(file);
  input.files = transfer.files;
}

function updatePreview(kind, input, image, fallbackKey) {
  const file = input.files?.[0];
  const zone = input.closest(".drop-zone");
  setFileName(input, kind === "top" ? topFileName : sideFileName, fallbackKey);

  if (state.previewUrls[kind]) {
    URL.revokeObjectURL(state.previewUrls[kind]);
    state.previewUrls[kind] = null;
  }

  if (kind === "top") {
    topBoxJson.value = "";
  } else {
    sideBoxJson.value = "";
  }

  if (!file) {
    image.removeAttribute("src");
    zone.classList.remove("has-preview");
    return;
  }

  state.previewUrls[kind] = URL.createObjectURL(file);
  image.src = state.previewUrls[kind];
  zone.classList.add("has-preview");
}

function cleanPayload(payload) {
  for (const key of [
    "side_image",
    "manual_height_mm",
    "camera_distance_mm",
    "focal_length_35mm",
    "top_box_json",
    "side_box_json",
    "order_id",
    "barcode_text",
  ]) {
    if (!payload.get(key)) {
      payload.delete(key);
    }
  }
  if (!sideImage.files?.length) {
    payload.delete("side_image");
  }
  if (!payload.get("order_id") && payload.get("barcode_text")) {
    payload.set("order_id", payload.get("barcode_text"));
  }
}

async function submitMeasurement(event) {
  event.preventDefault();
  setBusy(true);
  stopDrawing(false);
  qualityFlags.innerHTML = "";
  recommendations.innerHTML = "";

  const payload = new FormData(form);
  cleanPayload(payload);

  try {
    const response = await fetch("/api/measure", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    renderResult(data);
    await loadHistory();
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

async function loadDemoImage() {
  setBusy(true);
  try {
    const response = await fetch("/api/demo-image.jpg");
    if (!response.ok) {
      throw new Error(response.statusText);
    }
    const blob = await response.blob();
    const file = new File([blob], "packvision-demo-top.jpg", { type: "image/jpeg" });
    setInputFile(topImage, file);
    form.elements.manual_height_mm.value = "120";
    orderIdInput.value = `DEMO-${Date.now().toString().slice(-6)}`;
    topBoxJson.value = "";
    sideBoxJson.value = "";
    updatePreview("top", topImage, topPreview, "noFile");
    await submitMeasurement(new Event("submit", { cancelable: true }));
  } catch (error) {
    showError(error);
  } finally {
    setBusy(false);
  }
}

function showError(error) {
  state.lastResult = null;
  resultTitle.textContent = t("error");
  confidenceValue.textContent = "--";
  copyJsonButton.disabled = true;
  adjustTopButton.disabled = true;
  showTopViewButton.disabled = true;
  showSideViewButton.disabled = true;
  openImageLink.href = "#";
  openImageLink.setAttribute("aria-disabled", "true");
  recommendations.innerHTML = "";
  qualityFlags.innerHTML = "";
  sideSummary.textContent = "";
  const badge = document.createElement("span");
  badge.className = "flag";
  badge.textContent = String(error.message || error);
  qualityFlags.appendChild(badge);
}

function renderResult(data, options = {}) {
  state.lastResult = data;
  if (!options.keepView) {
    state.activeView = "top";
  }
  resultTitle.textContent = data.status === "measured" ? t("measured") : t("needsReference");
  confidenceValue.textContent = `${t("confidence")} ${Math.round((data.confidence || 0) * 100)}%`;
  metricEls.length_mm.textContent = formatMm(data.dimensions.length_mm);
  metricEls.width_mm.textContent = formatMm(data.dimensions.width_mm);
  metricEls.height_mm.textContent = formatMm(data.dimensions.height_mm);
  metricEls.volume_l.textContent = formatVolume(data.dimensions.volume_l);

  copyJsonButton.disabled = false;
  adjustTopButton.disabled = false;
  showTopViewButton.disabled = false;
  showSideViewButton.disabled = !data.side_view?.annotated_image_url;
  showTopViewButton.classList.toggle("is-active", state.activeView === "top");
  showSideViewButton.classList.toggle("is-active", state.activeView === "side");
  renderStageImage();
  renderSideSummary(data);
  renderFlags(data);
}

function renderStageImage() {
  const view = state.activeView === "side" ? state.lastResult?.side_view : state.lastResult?.top_view;
  const url = view?.annotated_image_url;
  showTopViewButton.classList.toggle("is-active", state.activeView === "top");
  showSideViewButton.classList.toggle("is-active", state.activeView === "side");
  if (url) {
    annotatedImage.src = url;
    annotatedImage.style.display = "block";
    emptyStage.style.display = "none";
    openImageLink.href = url;
    openImageLink.removeAttribute("aria-disabled");
    resizeCanvas();
  } else {
    annotatedImage.removeAttribute("src");
    annotatedImage.style.display = "none";
    emptyStage.style.display = "grid";
    openImageLink.href = "#";
    openImageLink.setAttribute("aria-disabled", "true");
  }
}

function renderSideSummary(data) {
  if (!data.side_measurement) {
    sideSummary.textContent = "";
    return;
  }
  const side = data.side_measurement;
  sideSummary.textContent = `${t("sideSummary")}: ${formatMm(side.height_candidate_mm)} (${side.scale_source})`;
}

function renderFlags(data) {
  qualityFlags.innerHTML = "";
  for (const flag of data.quality_flags || []) {
    const badge = document.createElement("span");
    badge.className = "flag";
    badge.textContent = labelFrom(flagLabels, flag);
    qualityFlags.appendChild(badge);
  }

  recommendations.innerHTML = "";
  for (const code of data.recommendation_codes || []) {
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = labelFrom(recommendationLabels, code);
    recommendations.appendChild(item);
  }
}

async function copyResultJson() {
  if (!state.lastResult) {
    return;
  }
  const text = JSON.stringify(state.lastResult, null, 2);
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
  const oldText = copyJsonButton.textContent;
  copyJsonButton.textContent = t("copied");
  setTimeout(() => {
    copyJsonButton.textContent = oldText;
  }, 1200);
}

async function normalizeScannerInput() {
  const payload = {
    order_id: orderIdInput.value,
    barcode_text: barcodeTextInput.value,
  };
  if (!payload.order_id && !payload.barcode_text) {
    return;
  }
  const response = await fetch("/api/orders/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  orderIdInput.value = data.order_id || "";
  barcodeTextInput.value = data.barcode_text || data.order_id || "";
}

async function decodeBarcodeImage() {
  const file = orderImage.files?.[0];
  if (!file) {
    return;
  }
  const oldText = decodeBarcodeButton.textContent;
  decodeBarcodeButton.textContent = t("decoding");
  decodeBarcodeButton.disabled = true;
  try {
    const payload = new FormData();
    payload.set("order_image", file);
    const response = await fetch("/api/orders/decode-image", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    const first = data.codes?.[0]?.text;
    if (first) {
      barcodeTextInput.value = first;
      if (!orderIdInput.value) {
        orderIdInput.value = first;
      }
      decodeBarcodeButton.textContent = t("barcodeFound");
    } else {
      decodeBarcodeButton.textContent = t("barcodeNotFound");
    }
  } catch (error) {
    decodeBarcodeButton.textContent = String(error.message || error);
  } finally {
    setTimeout(() => {
      decodeBarcodeButton.textContent = oldText;
      decodeBarcodeButton.disabled = false;
      orderImage.value = "";
    }, 1400);
  }
}

async function loadHistory() {
  const params = new URLSearchParams();
  if (historySearch.value.trim()) {
    params.set("order_id", historySearch.value.trim());
  }
  params.set("limit", "30");
  const response = await fetch(`/api/history?${params}`);
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  renderHistory(data.items || []);
}

function renderHistory(items) {
  historyList.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = t("noHistory");
    historyList.appendChild(empty);
    return;
  }
  for (const item of items) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "history-row";
    row.addEventListener("click", () => openHistoryItem(item.measurement_id));
    appendHistoryCell(row, item.order_id || item.barcode_text || item.measurement_id, formatDate(item.created_at), true);
    appendHistoryCell(row, item.status, `${Math.round((item.confidence || 0) * 100)}%`, false);
    appendHistoryCell(row, formatMm(item.length_mm), t("length"), false);
    appendHistoryCell(row, formatMm(item.width_mm), t("width"), false);
    appendHistoryCell(row, formatMm(item.height_mm), t("height"), false);
    appendHistoryCell(row, formatVolume(item.volume_l), t("volume"), false);
    historyList.appendChild(row);
  }
}

function appendHistoryCell(row, main, sub, strongMain) {
  const wrap = document.createElement("div");
  const mainEl = document.createElement(strongMain ? "strong" : "span");
  const subEl = document.createElement("span");
  mainEl.textContent = main || "--";
  subEl.textContent = sub || "";
  wrap.append(mainEl, subEl);
  row.appendChild(wrap);
}

async function openHistoryItem(measurementId) {
  const response = await fetch(`/api/history/${measurementId}`);
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  renderResult(data);
  document.querySelector("#measure").scrollIntoView({ behavior: "smooth", block: "start" });
}

function resizeCanvas() {
  const rect = imageStage.getBoundingClientRect();
  annotationCanvas.width = Math.max(1, Math.round(rect.width));
  annotationCanvas.height = Math.max(1, Math.round(rect.height));
  redrawCanvas();
}

function getImageRect() {
  if (!annotatedImage.naturalWidth || !annotatedImage.naturalHeight) {
    return null;
  }
  const stageWidth = annotationCanvas.width || imageStage.clientWidth;
  const stageHeight = annotationCanvas.height || imageStage.clientHeight;
  const imageRatio = annotatedImage.naturalWidth / annotatedImage.naturalHeight;
  let width = stageWidth;
  let height = width / imageRatio;
  if (height > stageHeight) {
    height = stageHeight;
    width = height * imageRatio;
  }
  return {
    left: (stageWidth - width) / 2,
    top: (stageHeight - height) / 2,
    width,
    height,
  };
}

function eventPoint(event) {
  const rect = annotationCanvas.getBoundingClientRect();
  const point = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
  const imageRect = getImageRect();
  if (!imageRect) {
    return point;
  }
  point.x = Math.max(imageRect.left, Math.min(imageRect.left + imageRect.width, point.x));
  point.y = Math.max(imageRect.top, Math.min(imageRect.top + imageRect.height, point.y));
  return point;
}

function toImagePoint(point) {
  const imageRect = getImageRect();
  if (!imageRect) {
    return [0, 0];
  }
  const x = ((point.x - imageRect.left) / imageRect.width) * annotatedImage.naturalWidth;
  const y = ((point.y - imageRect.top) / imageRect.height) * annotatedImage.naturalHeight;
  return [Math.round(x * 10) / 10, Math.round(y * 10) / 10];
}

function toggleDrawing() {
  if (!state.lastResult) {
    return;
  }
  state.drawing.active = !state.drawing.active;
  state.drawing.start = null;
  state.drawing.current = null;
  imageStage.classList.toggle("is-drawing", state.drawing.active);
  adjustTopButton.classList.toggle("is-active", state.drawing.active);
  resizeCanvas();
}

function stopDrawing(clearCanvas = true) {
  state.drawing.active = false;
  state.drawing.start = null;
  state.drawing.current = null;
  imageStage.classList.remove("is-drawing");
  adjustTopButton.classList.remove("is-active");
  if (clearCanvas) {
    redrawCanvas();
  }
}

function redrawCanvas() {
  const ctx = annotationCanvas.getContext("2d");
  ctx.clearRect(0, 0, annotationCanvas.width, annotationCanvas.height);
  if (!state.drawing.start || !state.drawing.current) {
    return;
  }
  const x = Math.min(state.drawing.start.x, state.drawing.current.x);
  const y = Math.min(state.drawing.start.y, state.drawing.current.y);
  const width = Math.abs(state.drawing.current.x - state.drawing.start.x);
  const height = Math.abs(state.drawing.current.y - state.drawing.start.y);
  ctx.fillStyle = "rgba(31, 122, 117, 0.16)";
  ctx.strokeStyle = "#e7c56c";
  ctx.lineWidth = 2;
  ctx.fillRect(x, y, width, height);
  ctx.strokeRect(x, y, width, height);
}

function finishManualBox() {
  const start = state.drawing.start;
  const current = state.drawing.current;
  if (!start || !current || Math.abs(current.x - start.x) < 8 || Math.abs(current.y - start.y) < 8) {
    stopDrawing();
    return;
  }
  const p1 = toImagePoint(start);
  const p2 = toImagePoint(current);
  const points = [
    [Math.min(p1[0], p2[0]), Math.min(p1[1], p2[1])],
    [Math.max(p1[0], p2[0]), Math.max(p1[1], p2[1])],
  ];
  if (state.activeView === "side") {
    sideBoxJson.value = JSON.stringify(points);
  } else {
    topBoxJson.value = JSON.stringify(points);
  }
  stopDrawing();
  const badge = document.createElement("span");
  badge.className = "flag";
  badge.textContent = t("manualBoxReady");
  qualityFlags.prepend(badge);
  submitMeasurement(new Event("submit", { cancelable: true }));
}

function wireDropZone(zone) {
  const kind = zone.dataset.dropZone;
  const input = kind === "top" ? topImage : sideImage;
  const preview = kind === "top" ? topPreview : sidePreview;
  const fallback = kind === "top" ? "noFile" : "optional";

  for (const eventName of ["dragenter", "dragover"]) {
    zone.addEventListener(eventName, (event) => {
      event.preventDefault();
      zone.classList.add("is-dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    zone.addEventListener(eventName, () => {
      zone.classList.remove("is-dragging");
    });
  }
  zone.addEventListener("drop", (event) => {
    event.preventDefault();
    const file = [...event.dataTransfer.files].find((item) => item.type.startsWith("image/"));
    if (!file) {
      return;
    }
    setInputFile(input, file);
    updatePreview(kind, input, preview, fallback);
  });
}

languageSelect.addEventListener("change", (event) => {
  state.lang = event.target.value;
  applyLanguage();
});

document.querySelectorAll("[data-theme-choice]").forEach((button) => {
  button.addEventListener("click", () => {
    state.theme = button.dataset.themeChoice;
    applyTheme();
  });
});

document.querySelectorAll("[data-drop-zone]").forEach(wireDropZone);
topImage.addEventListener("change", () => updatePreview("top", topImage, topPreview, "noFile"));
sideImage.addEventListener("change", () => updatePreview("side", sideImage, sidePreview, "optional"));
form.addEventListener("submit", submitMeasurement);
demoButton.addEventListener("click", loadDemoImage);
copyJsonButton.addEventListener("click", copyResultJson);
decodeBarcodeButton.addEventListener("click", () => orderImage.click());
orderImage.addEventListener("change", decodeBarcodeImage);
refreshHistoryButton.addEventListener("click", loadHistory);
historySearch.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    loadHistory();
  }
});
for (const input of [orderIdInput, barcodeTextInput]) {
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      normalizeScannerInput();
    }
  });
}
showTopViewButton.addEventListener("click", () => {
  state.activeView = "top";
  renderStageImage();
});
showSideViewButton.addEventListener("click", () => {
  if (!state.lastResult?.side_view?.annotated_image_url) {
    return;
  }
  state.activeView = "side";
  renderStageImage();
});
adjustTopButton.addEventListener("click", toggleDrawing);
annotatedImage.addEventListener("load", resizeCanvas);
window.addEventListener("resize", resizeCanvas);
annotationCanvas.addEventListener("pointerdown", (event) => {
  if (!state.drawing.active) {
    return;
  }
  annotationCanvas.setPointerCapture(event.pointerId);
  state.drawing.start = eventPoint(event);
  state.drawing.current = state.drawing.start;
  redrawCanvas();
});
annotationCanvas.addEventListener("pointermove", (event) => {
  if (!state.drawing.active || !state.drawing.start) {
    return;
  }
  state.drawing.current = eventPoint(event);
  redrawCanvas();
});
annotationCanvas.addEventListener("pointerup", finishManualBox);
annotationCanvas.addEventListener("pointercancel", () => stopDrawing());

applyLanguage();
applyTheme();
loadHistory();
