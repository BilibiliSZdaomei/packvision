const translations = {
  zh: {
    localLab: "本地仓库测量台",
    measure: "测量",
    depth: "深度",
    history: "历史",
    review: "复核",
    usage: "统计",
    calibration: "校准卡",
    localApi: "本地 API",
    project: "包装尺寸检测",
    title: "自动测量工作台",
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
    uploadSet: "扫码、上传、自动测量",
    printMarker: "打印标记",
    orderId: "单号",
    barcodeText: "扫码文本",
    decodeBarcode: "识别条码图片",
    partCategory: "备件类型",
    packageHint: "包装类型",
    materialHint: "材质/表面",
    optionalPartDetails: "可选补充信息",
    autoMeasureNoSelection: "不填也会自动判断包装和材质",
    autoPackage: "自动判断",
    autoMaterial: "自动/普通",
    carton: "标准纸箱",
    longPart: "长条件",
    irregular: "异形件",
    bulkyIrregular: "大件异形",
    softPack: "软包",
    reflectiveMaterial: "反光/金属",
    transparentMaterial: "透明/灯罩",
    darkMaterial: "深黑吸光",
    deformableMaterial: "易变形软材",
    actualWeight: "实重，kg",
    decoding: "识别中",
    barcodeFound: "已识别单号",
    barcodeNotFound: "未识别到条码",
    topPhoto: "顶部照片",
    sidePhoto: "侧面照片",
    noFile: "未选择文件",
    optional: "可选",
    measurementMode: "测量参数",
    estimateNote: "无卡模式需要距离和焦距，结果为估算。",
    advancedEstimateParams: "高级估算参数",
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
    reviewTitle: "失败和低置信样本池",
    refreshReview: "刷新复核",
    exportReview: "导出复核 CSV",
    exportReviewTruth: "导出真值模板",
    reviewSamples: "复核样本",
    highPriority: "高优先级",
    topReviewReason: "主要原因",
    noReview: "暂无需要复核的样本",
    suggestedAction: "建议动作",
    usageTitle: "后台使用与测量次数",
    refreshUsage: "刷新统计",
    exportUsage: "导出统计 CSV",
    totalCalls: "总调用",
    measurementCalls: "测量次数",
    failedCalls: "失败次数",
    todayMeasurements: "今日测量",
    successRate: "成功率",
    lastEvent: "最近调用",
    endpointBreakdown: "接口明细",
    noUsage: "暂无调用记录",
    refresh: "刷新",
    noHistory: "还没有匹配的历史记录",
    manualBoxReady: "手动框已应用",
    sideSummary: "侧面高度候选",
    industrySummary: "行业摘要",
    packageClass: "包装分类",
    materialClass: "材质风险",
    captureMode: "推荐采集",
    chargeableWeight: "计费重量",
    exportCsv: "导出 CSV",
    depthTitle: "Astra Pro 深度相机工作区",
    refreshDepth: "刷新状态",
    probeDepthCapture: "采集探测",
    workflowGuide: "调试清单",
    autoWorkflow: "自动识别流程",
    arrivalKit: "到货准备",
    captureSteps: "采集步骤",
    cameraCount: "相机数",
    motherboard: "主板",
    required: "需要",
    notRequired: "暂不需要",
    validationPlan: "验收计划",
    validationTemplate: "验收模板",
    aiPlugins: "AI 插件",
    aiPluginStatus: "插件状态",
    aiPluginReady: "可用插件",
    aiPluginAttention: "需处理",
    aiPluginPolicy: "基础包不内置重模型",
    aiPluginNoPlugins: "未安装 AI 插件，继续使用深度/手动复核兜底",
    minSamples: "最少样本",
    tolerance: "容差",
    toleranceTemplate: "≤ {mm} mm 或 ≤ {pct}% 最大尺寸误差",
    totalSamples: "总样本",
    runDepthDemo: "运行深度演示",
    saveDepthDemo: "保存演示记录",
    savedToHistory: "已保存到历史",
    depthBackend: "推荐后端",
    depthDriver: "驱动状态",
    depthOpenNi: "OpenNI2",
    depthPyorbbec: "pyorbbecsdk",
    depthConfiguredCameras: "配置相机",
    depthDetectedDevices: "已连接设备",
    depthThreeView: "三视图",
    captureProbe: "采集探测",
    captureStatus: "采集状态",
    selectedBackend: "选中后端",
    nextAction: "下一步",
    depthDemo: "深度演示",
    demoObject: "异形件样本",
    ready: "可用",
    missing: "未就绪",
    installed: "已安装",
    unavailable: "不可用",
  },
  en: {
    localLab: "Local warehouse station",
    measure: "Measure",
    depth: "Depth",
    history: "History",
    review: "Review",
    usage: "Usage",
    calibration: "Calibration",
    localApi: "Local API",
    project: "Packaging dimension detection",
    title: "Automatic measurement workstation",
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
    uploadSet: "Scan, upload, measure",
    printMarker: "Print marker",
    orderId: "Order ID",
    barcodeText: "Scanned text",
    decodeBarcode: "Decode barcode image",
    partCategory: "Part category",
    packageHint: "Package type",
    materialHint: "Material",
    optionalPartDetails: "Optional details",
    autoMeasureNoSelection: "Leave blank; package and material are auto-detected",
    autoPackage: "Auto",
    autoMaterial: "Auto / normal",
    carton: "Carton",
    longPart: "Long part",
    irregular: "Irregular",
    bulkyIrregular: "Bulky irregular",
    softPack: "Soft pack",
    reflectiveMaterial: "Reflective / metal",
    transparentMaterial: "Transparent / lens",
    darkMaterial: "Dark absorbing",
    deformableMaterial: "Deformable",
    actualWeight: "Weight, kg",
    decoding: "Decoding",
    barcodeFound: "Order detected",
    barcodeNotFound: "No barcode detected",
    topPhoto: "Top photo",
    sidePhoto: "Side photo",
    noFile: "No file selected",
    optional: "Optional",
    measurementMode: "Measurement parameters",
    estimateNote: "No-card mode needs distance and focal length; results are estimates.",
    advancedEstimateParams: "Advanced estimate parameters",
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
    reviewTitle: "Failure and low-confidence sample pool",
    refreshReview: "Refresh review",
    exportReview: "Export review CSV",
    exportReviewTruth: "Export truth template",
    reviewSamples: "Review samples",
    highPriority: "High priority",
    topReviewReason: "Top reason",
    noReview: "No review samples yet",
    suggestedAction: "Suggested action",
    usageTitle: "Backend usage and measurement counts",
    refreshUsage: "Refresh usage",
    exportUsage: "Export usage CSV",
    totalCalls: "Total calls",
    measurementCalls: "Measurements",
    failedCalls: "Failures",
    todayMeasurements: "Today",
    successRate: "Success rate",
    lastEvent: "Last call",
    endpointBreakdown: "Endpoint breakdown",
    noUsage: "No usage records yet",
    refresh: "Refresh",
    noHistory: "No matching history yet",
    manualBoxReady: "Manual box applied",
    sideSummary: "Side height candidate",
    industrySummary: "Industry summary",
    packageClass: "Package class",
    materialClass: "Material risk",
    captureMode: "Capture mode",
    chargeableWeight: "Chargeable weight",
    exportCsv: "Export CSV",
    depthTitle: "Astra Pro depth camera workspace",
    refreshDepth: "Refresh status",
    probeDepthCapture: "Probe capture",
    workflowGuide: "Setup guide",
    autoWorkflow: "Auto workflow",
    arrivalKit: "Arrival kit",
    captureSteps: "Capture steps",
    cameraCount: "Cameras",
    motherboard: "Motherboard",
    required: "Required",
    notRequired: "Not needed",
    validationPlan: "Trial plan",
    validationTemplate: "Trial CSV",
    aiPlugins: "AI plugins",
    aiPluginStatus: "Plugin status",
    aiPluginReady: "Ready plugins",
    aiPluginAttention: "Needs attention",
    aiPluginPolicy: "Base package ships without heavy models",
    aiPluginNoPlugins: "No AI plugins installed; depth/manual fallback remains active",
    minSamples: "Min samples",
    tolerance: "Tolerance",
    toleranceTemplate: "≤ {mm} mm or ≤ {pct}% max dimension error",
    totalSamples: "Total samples",
    runDepthDemo: "Run depth demo",
    saveDepthDemo: "Save demo record",
    savedToHistory: "Saved to history",
    depthBackend: "Recommended backend",
    depthDriver: "Driver status",
    depthOpenNi: "OpenNI2",
    depthPyorbbec: "pyorbbecsdk",
    depthConfiguredCameras: "Configured cameras",
    depthDetectedDevices: "Connected devices",
    depthThreeView: "Three-view",
    captureProbe: "Capture probe",
    captureStatus: "Capture status",
    selectedBackend: "Selected backend",
    nextAction: "Next action",
    depthDemo: "Depth demo",
    demoObject: "Irregular sample",
    ready: "Ready",
    missing: "Missing",
    installed: "Installed",
    unavailable: "Unavailable",
  },
  uk: {
    localLab: "Локальна станція складу",
    measure: "Вимір",
    depth: "Глибина",
    history: "Історія",
    review: "Перевірка",
    usage: "Статистика",
    calibration: "Калібрування",
    localApi: "Локальний API",
    project: "Вимірювання пакування",
    title: "Автоматична станція вимірювання",
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
    uploadSet: "Скан, фото, вимір",
    printMarker: "Друк маркера",
    orderId: "Номер",
    barcodeText: "Текст скану",
    decodeBarcode: "Зчитати штрихкод",
    partCategory: "Тип деталі",
    packageHint: "Тип пакування",
    materialHint: "Матеріал",
    optionalPartDetails: "Додатково",
    autoMeasureNoSelection: "Можна не заповнювати; тип і матеріал визначаються автоматично",
    autoPackage: "Авто",
    autoMaterial: "Авто / звичайний",
    carton: "Коробка",
    longPart: "Довга деталь",
    irregular: "Нерівна",
    bulkyIrregular: "Габаритна нерівна",
    softPack: "М'який пак",
    reflectiveMaterial: "Відбивний / метал",
    transparentMaterial: "Прозорий / лінза",
    darkMaterial: "Темний поглинаючий",
    deformableMaterial: "Деформівний",
    actualWeight: "Вага, кг",
    decoding: "Зчитування",
    barcodeFound: "Номер знайдено",
    barcodeNotFound: "Штрихкод не знайдено",
    topPhoto: "Фото зверху",
    sidePhoto: "Фото збоку",
    noFile: "Файл не вибрано",
    optional: "Необов'язково",
    measurementMode: "Параметри",
    estimateNote: "Без картки потрібні відстань і фокус; це оцінка.",
    advancedEstimateParams: "Розширені параметри",
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
    reviewTitle: "Зразки помилок і низької довіри",
    refreshReview: "Оновити перевірку",
    exportReview: "Експорт CSV",
    exportReviewTruth: "Експорт шаблону",
    reviewSamples: "Зразки перевірки",
    highPriority: "Високий пріоритет",
    topReviewReason: "Головна причина",
    noReview: "Немає зразків для перевірки",
    suggestedAction: "Рекомендована дія",
    usageTitle: "Використання та кількість вимірювань",
    refreshUsage: "Оновити статистику",
    exportUsage: "Експорт CSV",
    totalCalls: "Усього викликів",
    measurementCalls: "Вимірювання",
    failedCalls: "Помилки",
    todayMeasurements: "Сьогодні",
    successRate: "Успішність",
    lastEvent: "Останній виклик",
    endpointBreakdown: "За endpoint",
    noUsage: "Записів використання ще немає",
    refresh: "Оновити",
    noHistory: "Записів ще немає",
    manualBoxReady: "Рамку застосовано",
    sideSummary: "Кандидат висоти збоку",
    industrySummary: "Галузевий підсумок",
    packageClass: "Клас пакування",
    materialClass: "Ризик матеріалу",
    captureMode: "Режим зйомки",
    chargeableWeight: "Платна вага",
    exportCsv: "Експорт CSV",
    depthTitle: "Робоча зона Astra Pro",
    refreshDepth: "Оновити статус",
    probeDepthCapture: "Перевірити збір",
    workflowGuide: "Підготовка",
    autoWorkflow: "Авто процес",
    arrivalKit: "Комплект",
    captureSteps: "Кроки зйомки",
    cameraCount: "Камери",
    motherboard: "Плата",
    required: "Потрібно",
    notRequired: "Не потрібно",
    validationPlan: "План приймання",
    validationTemplate: "CSV приймання",
    aiPlugins: "AI плагіни",
    aiPluginStatus: "Стан плагінів",
    aiPluginReady: "Готові плагіни",
    aiPluginAttention: "Потрібна увага",
    aiPluginPolicy: "Базовий пакет без важких моделей",
    aiPluginNoPlugins: "AI плагіни не встановлені; працює ручний/глибинний резерв",
    minSamples: "Мін. зразків",
    tolerance: "Допуск",
    toleranceTemplate: "≤ {mm} мм або ≤ {pct}% макс. похибка",
    totalSamples: "Усього зразків",
    runDepthDemo: "Запустити демо",
    saveDepthDemo: "Зберегти демо",
    savedToHistory: "Збережено в історії",
    depthBackend: "Рекомендований бекенд",
    depthDriver: "Стан драйвера",
    depthOpenNi: "OpenNI2",
    depthPyorbbec: "pyorbbecsdk",
    depthConfiguredCameras: "Налаштовані камери",
    depthDetectedDevices: "Підключені пристрої",
    depthThreeView: "Три ракурси",
    captureProbe: "Перевірка збору",
    captureStatus: "Стан збору",
    selectedBackend: "Обраний бекенд",
    nextAction: "Наступний крок",
    depthDemo: "Демо глибини",
    demoObject: "Нерівний зразок",
    ready: "Готово",
    missing: "Немає",
    installed: "Встановлено",
    unavailable: "Недоступно",
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
    depth_camera_measurement: "深度相机测量",
    depth_roi_used: "深度 ROI 测量",
    depth_object_mask_used: "深度异形掩膜",
    background_depth_used: "使用台面深度",
    background_depth_missing: "缺少台面深度",
    axis_aligned_extent_used: "按水平/垂直外接范围测量",
    principal_axis_extent_used: "按主轴方向测量长条件",
    depth_outliers_trimmed: "深度离群点已裁剪",
    point_cloud_extent_trimmed: "点云范围已裁剪",
    small_object_mask: "目标掩膜偏小",
    sparse_depth_roi: "深度 ROI 有效点偏少",
    sparse_depth_frame: "深度帧有效点偏少",
    depth_hole_risk: "深度孔洞风险",
    noisy_depth_roi: "深度 ROI 噪声偏高",
    unstable_table_depth: "台面深度不稳定",
    no_valid_depth_roi: "ROI 内无有效深度",
    reflective_depth_noise_risk: "反光材质深度噪声风险",
    transparent_depth_dropout_risk: "透明材质深度丢失风险",
    dark_surface_depth_dropout_risk: "深黑材质深度丢失风险",
    deformable_shape_drift_risk: "软材形变风险",
    lighting_overexposed: "光照过曝",
    lighting_underexposed: "光线不足",
    low_contrast_capture: "画面对比度过低",
    blurry_capture: "照片模糊",
    manual_review_recommended: "建议人工复核",
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
    depth_camera_measurement: "Depth camera measurement",
    depth_roi_used: "Depth ROI used",
    depth_object_mask_used: "Depth object mask",
    background_depth_used: "Table depth used",
    background_depth_missing: "Table depth missing",
    axis_aligned_extent_used: "Axis-aligned extent used",
    principal_axis_extent_used: "Principal-axis extent used",
    depth_outliers_trimmed: "Depth outliers trimmed",
    point_cloud_extent_trimmed: "Point-cloud extent trimmed",
    small_object_mask: "Small object mask",
    sparse_depth_roi: "Sparse depth ROI",
    sparse_depth_frame: "Sparse depth frame",
    depth_hole_risk: "Depth-hole risk",
    noisy_depth_roi: "Noisy depth ROI",
    unstable_table_depth: "Unstable table depth",
    no_valid_depth_roi: "No valid depth in ROI",
    reflective_depth_noise_risk: "Reflective depth-noise risk",
    transparent_depth_dropout_risk: "Transparent depth-dropout risk",
    dark_surface_depth_dropout_risk: "Dark-surface dropout risk",
    deformable_shape_drift_risk: "Deformable-shape drift risk",
    lighting_overexposed: "Overexposed capture",
    lighting_underexposed: "Low-light capture",
    low_contrast_capture: "Low contrast capture",
    blurry_capture: "Blurry capture",
    manual_review_recommended: "Manual review recommended",
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
    depth_camera_measurement: "Вимір камерою глибини",
    depth_roi_used: "ROI глибини",
    depth_object_mask_used: "Маска об'єкта",
    background_depth_used: "Глибина столу",
    background_depth_missing: "Немає глибини столу",
    axis_aligned_extent_used: "Вісьове обмеження",
    principal_axis_extent_used: "Головна вісь об'єкта",
    depth_outliers_trimmed: "Викиди глибини обрізано",
    point_cloud_extent_trimmed: "Хмару точок обрізано",
    small_object_mask: "Мала маска об'єкта",
    sparse_depth_roi: "Рідкісні точки ROI глибини",
    sparse_depth_frame: "Рідкісні точки кадру глибини",
    depth_hole_risk: "Ризик отворів глибини",
    noisy_depth_roi: "Шумний ROI глибини",
    unstable_table_depth: "Нестабільна глибина столу",
    no_valid_depth_roi: "Немає валідної глибини в ROI",
    reflective_depth_noise_risk: "Ризик шуму від відблиску",
    transparent_depth_dropout_risk: "Ризик втрати глибини прозорого",
    dark_surface_depth_dropout_risk: "Ризик втрати темної поверхні",
    deformable_shape_drift_risk: "Ризик деформації форми",
    lighting_overexposed: "Пересвітлене фото",
    lighting_underexposed: "Недостатнє світло",
    low_contrast_capture: "Низький контраст",
    blurry_capture: "Розмите фото",
    manual_review_recommended: "Потрібна ручна перевірка",
  },
};

const recommendationLabels = {
  zh: {
    add_height_or_side_photo: "补充侧面照片，或在人工高度中输入真实高度。",
    distance_mode_is_estimate: "无卡估算会受拍摄距离、焦距和透视影响，建议抽检复核。",
    keep_camera_top_down: "顶部照尽量垂直拍摄，减少透视带来的长宽误差。",
    move_camera_closer: "包装占画面比例偏小，建议靠近一点重新拍摄。",
    place_or_print_marker: "要高精度，请打印校准卡并把标记放在包装同一平面。",
    retake_away_from_direct_light: "避开阳光直射或强反光位置后重拍。",
    add_stable_indoor_light: "补充稳定室内光线后重拍。",
    retake_on_plain_background: "换成更干净的背景，并保证边缘清晰。",
    stabilize_camera_or_tripod: "固定手机/相机后重拍，避免手抖。",
    use_distance_mode_or_marker: "没有标记时，可以输入相机距离和等效焦距进行估算。",
    retake_depth_with_less_reflection: "调整角度避开反光/透明区域，必要时贴哑光胶带后重采深度。",
    stabilize_depth_camera_and_retake: "固定深度相机与工件，等待画面稳定后重新采集。",
    select_clean_background_roi: "重新选择平整干净的台面背景区域。",
    expand_object_roi_or_reposition: "扩大目标框或重新摆放工件，让异形件主体进入 ROI。",
  },
  en: {
    add_height_or_side_photo: "Add a side photo or type the real height manually.",
    distance_mode_is_estimate: "No-card mode is affected by distance, focal length, and perspective; spot-check it.",
    keep_camera_top_down: "Use a top-down angle to reduce perspective error.",
    move_camera_closer: "The parcel is small in frame; retake closer if possible.",
    place_or_print_marker: "For higher precision, print the calibration card and place it on the same plane.",
    retake_away_from_direct_light: "Retake away from direct sunlight or harsh reflections.",
    add_stable_indoor_light: "Add stable indoor lighting and retake.",
    retake_on_plain_background: "Use a cleaner background with clearer parcel edges.",
    stabilize_camera_or_tripod: "Stabilize the phone/camera and retake.",
    use_distance_mode_or_marker: "Without a marker, enter camera distance and 35mm focal length for estimation.",
    retake_depth_with_less_reflection: "Adjust the angle away from reflections or transparent areas; use matte tape if needed.",
    stabilize_depth_camera_and_retake: "Fix the depth camera and part, wait for a stable frame, then recapture.",
    select_clean_background_roi: "Select a flatter, cleaner table/background ROI.",
    expand_object_roi_or_reposition: "Expand the object ROI or reposition the part so the irregular body is inside it.",
  },
  uk: {
    add_height_or_side_photo: "Додайте бічне фото або введіть реальну висоту.",
    distance_mode_is_estimate: "Режим без картки залежить від відстані, фокуса і перспективи.",
    keep_camera_top_down: "Знімайте зверху, щоб зменшити похибку перспективи.",
    move_camera_closer: "Об'єкт малий у кадрі; зніміть ближче.",
    place_or_print_marker: "Для точності надрукуйте картку калібрування.",
    retake_away_from_direct_light: "Перезніміть без прямого сонця чи відблисків.",
    add_stable_indoor_light: "Додайте стабільне світло і перезніміть.",
    retake_on_plain_background: "Використайте чистіший фон і чіткі краї.",
    stabilize_camera_or_tripod: "Зафіксуйте телефон/камеру і перезніміть.",
    use_distance_mode_or_marker: "Без маркера введіть відстань камери та фокус 35 мм.",
    retake_depth_with_less_reflection: "Змініть кут від відблисків або прозорих зон; за потреби використайте матову стрічку.",
    stabilize_depth_camera_and_retake: "Зафіксуйте камеру глибини й деталь, дочекайтесь стабільного кадру та повторіть.",
    select_clean_background_roi: "Виберіть рівнішу й чистішу ділянку столу як фон.",
    expand_object_roi_or_reposition: "Розширте ROI або переставте деталь, щоб нерівний корпус потрапив у кадр.",
  },
};

const packageClassLabels = {
  zh: {
    standard_carton: "标准纸箱",
    long_part: "长条件",
    irregular_or_soft_pack: "异形/软包",
    bulky_irregular: "大件异形",
  },
  en: {
    standard_carton: "Standard carton",
    long_part: "Long part",
    irregular_or_soft_pack: "Irregular / soft pack",
    bulky_irregular: "Bulky irregular",
  },
  uk: {
    standard_carton: "Стандартна коробка",
    long_part: "Довга деталь",
    irregular_or_soft_pack: "Нерівне / м'яке",
    bulky_irregular: "Габаритне нерівне",
  },
};

const scenarioLabels = {
  zh: {
    standard_carton: "标准纸箱",
    long_part: "长条件",
    irregular_or_soft_pack: "异形/软包",
    bulky_irregular: "大件异形",
    reflective: "反光材质",
    transparent: "透明材质",
    dark_absorbing: "深黑吸光",
    deformable: "易变形材质",
  },
  en: {
    standard_carton: "Standard carton",
    long_part: "Long part",
    irregular_or_soft_pack: "Irregular / soft pack",
    bulky_irregular: "Bulky irregular",
    reflective: "Reflective material",
    transparent: "Transparent material",
    dark_absorbing: "Dark absorbing",
    deformable: "Deformable material",
  },
  uk: {
    standard_carton: "Стандартна коробка",
    long_part: "Довга деталь",
    irregular_or_soft_pack: "Нерівне / м'яке",
    bulky_irregular: "Габаритне нерівне",
    reflective: "Відбивний матеріал",
    transparent: "Прозорий матеріал",
    dark_absorbing: "Темний поглинаючий",
    deformable: "Деформівний матеріал",
  },
};

const materialClassLabels = {
  zh: {
    normal: "普通材质",
    reflective: "高风险：反光",
    transparent: "高风险：透明",
    dark_absorbing: "中风险：深黑吸光",
    deformable: "中风险：易变形",
  },
  en: {
    normal: "Normal",
    reflective: "High risk: reflective",
    transparent: "High risk: transparent",
    dark_absorbing: "Medium risk: dark absorbing",
    deformable: "Medium risk: deformable",
  },
  uk: {
    normal: "Звичайний",
    reflective: "Високий ризик: відбивний",
    transparent: "Високий ризик: прозорий",
    dark_absorbing: "Середній ризик: темний",
    deformable: "Середній ризик: деформівний",
  },
};

const captureModeLabels = {
  zh: {
    top_plus_side_or_depth_roi: "顶部+侧面或深度 ROI",
    depth_roi_long_item: "长条件深度 ROI",
    depth_object_mask: "深度异形掩膜",
    manual_review: "人工复核",
  },
  en: {
    top_plus_side_or_depth_roi: "Top + side or depth ROI",
    depth_roi_long_item: "Long-item depth ROI",
    depth_object_mask: "Depth object mask",
    manual_review: "Manual review",
  },
  uk: {
    top_plus_side_or_depth_roi: "Верх + бік або ROI",
    depth_roi_long_item: "ROI довгої деталі",
    depth_object_mask: "Маска глибини",
    manual_review: "Ручна перевірка",
  },
};

const cameraPoseLabels = {
  zh: {
    standard_carton: "顶部深度 ROI，侧面照或深度高度复核",
    long_part: "抬高俯拍或斜拍，保证完整长度进入画面",
    irregular_or_soft_pack: "深度对象掩膜采集，人工复核边界",
    bulky_irregular: "大范围 ROI，轮廓不完整时第二角度复核",
  },
  en: {
    standard_carton: "Top-down depth ROI with optional side-view height cross-check",
    long_part: "Raised top-down or oblique view covering the full length",
    irregular_or_soft_pack: "Object-mask depth capture with manual boundary review",
    bulky_irregular: "Wide ROI with a second-angle check when the silhouette is incomplete",
  },
  uk: {
    standard_carton: "Верхній ROI глибини з бічною перевіркою висоти",
    long_part: "Піднятий або косий вид з повною довжиною в кадрі",
    irregular_or_soft_pack: "Маска об'єкта з ручною перевіркою меж",
    bulky_irregular: "Широкий ROI і другий кут, якщо контур неповний",
  },
};

const probeStatusLabels = {
  zh: {
    ready_for_capture: "可采集",
    driver_ready_capture_backend_missing: "驱动就绪，采集后端待接入",
    capture_backend_missing: "采集后端未就绪",
    hardware_validation_required: "需要连接相机验证",
  },
  en: {
    ready_for_capture: "Ready for capture",
    driver_ready_capture_backend_missing: "Driver ready, capture backend pending",
    capture_backend_missing: "Capture backend missing",
    hardware_validation_required: "Hardware validation required",
  },
  uk: {
    ready_for_capture: "Готово до збору",
    driver_ready_capture_backend_missing: "Драйвер готовий, бекенд очікує",
    capture_backend_missing: "Бекенд збору відсутній",
    hardware_validation_required: "Потрібна перевірка камери",
  },
};

const probeActionLabels = {
  zh: {
    connect_camera_driver: "连接 Astra Pro，并确认 Windows 驱动已安装。",
    confirm_vendor_viewer_streams: "先打开上位机，确认 RGB 和 Depth 都有画面。",
    validate_known_carton_history: "用已知尺寸纸箱试测，并保存到历史记录。",
    confirm_vendor_viewer_depth: "连接 Astra Pro，并确认上位机能看到深度画面。",
    rerun_probe_connected: "相机连接后再次运行采集探测。",
    install_pyorbbec_if_unstable: "如果 OpenNI2 采集不稳定，再安装 pyorbbecsdk。",
    use_depth_frame_apis: "继续用现有 depth_frame 接口导入深度帧测量。",
    install_pyorbbec_hardware_build: "相机到货后再做包含 pyorbbecsdk 的硬件版构建。",
    run_status_script: "运行 scripts\\check_astra_depth_status.ps1 复核资料和驱动。",
    install_windows_driver: "先安装店铺教程里的 Astra Pro Windows 驱动。",
    set_astra_root: "如果资料目录变了，设置 PACKVISION_ASTRA_ROOT。",
    confirm_vendor_viewer: "先用上位机确认相机能正常出图。",
  },
  en: {
    connect_camera_driver: "Connect Astra Pro and confirm the Windows driver is installed.",
    confirm_vendor_viewer_streams: "Open the vendor viewer and confirm both RGB and Depth streams.",
    validate_known_carton_history: "Test a known carton and save the result to history.",
    confirm_vendor_viewer_depth: "Connect Astra Pro and confirm the vendor viewer can see depth frames.",
    rerun_probe_connected: "Run the capture probe again with the camera connected.",
    install_pyorbbec_if_unstable: "Install pyorbbecsdk later if OpenNI2 capture is unstable.",
    use_depth_frame_apis: "Keep using the current depth_frame APIs for imported depth frames.",
    install_pyorbbec_hardware_build: "Build a hardware edition with pyorbbecsdk after the camera arrives.",
    run_status_script: "Run scripts\\check_astra_depth_status.ps1 to recheck files and drivers.",
    install_windows_driver: "Install the Astra Pro Windows driver from the seller tutorial folder.",
    set_astra_root: "Set PACKVISION_ASTRA_ROOT if the tutorial folder moved.",
    confirm_vendor_viewer: "Confirm the camera streams in the vendor viewer first.",
  },
  uk: {
    connect_camera_driver: "Підключіть Astra Pro і перевірте драйвер Windows.",
    confirm_vendor_viewer_streams: "Відкрийте переглядач постачальника і перевірте RGB та Depth.",
    validate_known_carton_history: "Перевірте коробку відомого розміру і збережіть в історію.",
    confirm_vendor_viewer_depth: "Підключіть Astra Pro і перевірте глибину у переглядачі.",
    rerun_probe_connected: "Запустіть перевірку ще раз з підключеною камерою.",
    install_pyorbbec_if_unstable: "Встановіть pyorbbecsdk, якщо OpenNI2 працює нестабільно.",
    use_depth_frame_apis: "Використовуйте поточні depth_frame API для імпортованих кадрів.",
    install_pyorbbec_hardware_build: "Після прибуття камери зробіть збірку з pyorbbecsdk.",
    run_status_script: "Запустіть scripts\\check_astra_depth_status.ps1 для повторної перевірки.",
    install_windows_driver: "Встановіть драйвер Astra Pro Windows з матеріалів продавця.",
    set_astra_root: "Задайте PACKVISION_ASTRA_ROOT, якщо папку матеріалів перенесено.",
    confirm_vendor_viewer: "Спершу перевірте потоки камери у переглядачі.",
  },
};

const workflowLabels = {
  zh: {
    administrator_rights: "Windows 管理员权限",
    orbbec_viewer_driver: "Orbbec 驱动和上位机",
    usb_data_extension_cable: "USB 数据延长线",
    powered_usb_hub: "有源 USB 3.0 Hub",
    stable_mount_or_tripod: "三脚架/固定支架",
    truth_measurement_tools: "卷尺/游标卡尺",
    matte_work_surface: "哑光平整桌面",
    lighting_control: "稳定室内光线",
    barcode_input_ready: "扫码枪或条码图片入口",
    vendor_viewer_depth_check: "官方上位机深度图检查",
    top_depth_roi: "顶部深度 ROI",
    side_height_cross_check: "侧面高度交叉复核",
    long_item_depth_roi: "长条件深度 ROI",
    end_to_end_truth_check: "端到端人工真值复核",
    object_mask_depth_capture: "异形件深度掩膜采集",
    manual_mask_review: "人工复核掩膜边界",
    wide_roi_depth_capture: "大范围深度 ROI 采集",
    second_angle_cross_check: "第二角度交叉复核",
    separate_usb_controller_or_powered_hub_check: "不同 USB 口或有源 Hub 检查",
    reflective_surface_cross_check: "反光表面交叉复核",
    transparent_depth_dropout_review: "透明材质深度空洞复核",
    dark_surface_depth_dropout_review: "深色材质深度空洞复核",
    deformable_shape_repeat_capture: "易变形件重复采集",
    manual_review_required: "人工复核",
    direct_usb_port: "电脑直连 USB 口",
    short_data_cable: "短数据线",
    separate_pc_usb_ports: "不同电脑 USB 口",
    install_orbbec_driver: "安装 Orbbec 驱动",
    open_vendor_viewer: "打开官方上位机",
    confirm_depth_frame: "确认深度画面",
    run_packvision_depth_status: "运行 PackVision 深度状态",
    probe_capture_backend: "探测采集后端",
    measure_validation_csv_samples: "采集验收 CSV 样本",
  },
  en: {
    administrator_rights: "Windows administrator rights",
    orbbec_viewer_driver: "Orbbec driver and viewer",
    usb_data_extension_cable: "USB data extension cables",
    powered_usb_hub: "Powered USB 3.0 hub",
    stable_mount_or_tripod: "Tripod or fixed mount",
    truth_measurement_tools: "Tape measure and caliper",
    matte_work_surface: "Flat matte work surface",
    lighting_control: "Stable indoor lighting",
    barcode_input_ready: "Scanner or barcode upload",
    vendor_viewer_depth_check: "Vendor viewer depth check",
    top_depth_roi: "Top depth ROI",
    side_height_cross_check: "Side-height cross-check",
    long_item_depth_roi: "Long-item depth ROI",
    end_to_end_truth_check: "End-to-end truth check",
    object_mask_depth_capture: "Irregular object-mask depth capture",
    manual_mask_review: "Manual mask boundary review",
    wide_roi_depth_capture: "Wide depth ROI capture",
    second_angle_cross_check: "Second-angle cross-check",
    separate_usb_controller_or_powered_hub_check: "Separate USB port or powered hub",
    reflective_surface_cross_check: "Reflective surface cross-check",
    transparent_depth_dropout_review: "Transparent depth-dropout review",
    dark_surface_depth_dropout_review: "Dark-surface depth-dropout review",
    deformable_shape_repeat_capture: "Repeat capture for deformable parts",
    manual_review_required: "Manual review",
    direct_usb_port: "Direct PC USB port",
    short_data_cable: "Short data cable",
    separate_pc_usb_ports: "Separate PC USB ports",
    install_orbbec_driver: "Install Orbbec driver",
    open_vendor_viewer: "Open vendor viewer",
    confirm_depth_frame: "Confirm depth frame",
    run_packvision_depth_status: "Run PackVision depth status",
    probe_capture_backend: "Probe capture backend",
    measure_validation_csv_samples: "Capture validation CSV samples",
  },
  uk: {
    administrator_rights: "Права адміністратора Windows",
    orbbec_viewer_driver: "Драйвер і переглядач Orbbec",
    usb_data_extension_cable: "USB кабелі даних",
    powered_usb_hub: "USB 3.0 Hub з живленням",
    stable_mount_or_tripod: "Штатив або кріплення",
    truth_measurement_tools: "Рулетка і штангенциркуль",
    matte_work_surface: "Матова рівна поверхня",
    lighting_control: "Стабільне освітлення",
    barcode_input_ready: "Сканер або фото штрихкоду",
    vendor_viewer_depth_check: "Перевірка глибини у Viewer",
    top_depth_roi: "Верхній ROI глибини",
    side_height_cross_check: "Бічна перевірка висоти",
    long_item_depth_roi: "ROI довгої деталі",
    end_to_end_truth_check: "Контроль ручного еталона",
    object_mask_depth_capture: "Маска нерівного об'єкта",
    manual_mask_review: "Ручна перевірка меж маски",
    wide_roi_depth_capture: "Широкий ROI глибини",
    second_angle_cross_check: "Перевірка з другого кута",
    separate_usb_controller_or_powered_hub_check: "Окремий USB або Hub",
    reflective_surface_cross_check: "Перевірка відблиску",
    transparent_depth_dropout_review: "Перевірка втрати глибини прозорого",
    dark_surface_depth_dropout_review: "Перевірка втрати глибини темного",
    deformable_shape_repeat_capture: "Повторний знімок деформівного",
    manual_review_required: "Ручна перевірка",
    direct_usb_port: "Прямий USB порт ПК",
    short_data_cable: "Короткий кабель даних",
    separate_pc_usb_ports: "Окремі USB порти ПК",
    install_orbbec_driver: "Встановити драйвер Orbbec",
    open_vendor_viewer: "Відкрити Viewer",
    confirm_depth_frame: "Підтвердити кадр глибини",
    run_packvision_depth_status: "Запустити статус глибини PackVision",
    probe_capture_backend: "Перевірити бекенд збору",
    measure_validation_csv_samples: "Зняти зразки CSV приймання",
  },
};

const localeMap = { zh: "zh-CN", en: "en-US", uk: "uk-UA" };

const state = {
  lang: localStorage.getItem("packvision.lang") || "zh",
  theme: localStorage.getItem("packvision.theme") || "light",
  lastResult: null,
  depthStatus: null,
  depthProbe: null,
  depthWorkflow: null,
  validationPlan: null,
  aiPlugins: null,
  usageSummary: null,
  reviewSamples: null,
  lastDepthDemo: null,
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
const industrySummary = document.querySelector("#industrySummary");
const depthStatusGrid = document.querySelector("#depthStatusGrid");
const refreshDepthStatusButton = document.querySelector("#refreshDepthStatusButton");
const probeDepthCaptureButton = document.querySelector("#probeDepthCaptureButton");
const loadDepthWorkflowButton = document.querySelector("#loadDepthWorkflowButton");
const workflowAutoSummary = document.querySelector("#workflowAutoSummary");
const workflowPackageSelect = document.querySelector("#workflowPackageSelect");
const workflowMaterialSelect = document.querySelector("#workflowMaterialSelect");
const workflowCameraCountSelect = document.querySelector("#workflowCameraCountSelect");
const loadValidationPlanButton = document.querySelector("#loadValidationPlanButton");
const runDepthDemoButton = document.querySelector("#runDepthDemoButton");
const saveDepthDemoButton = document.querySelector("#saveDepthDemoButton");
const loadAiPluginsButton = document.querySelector("#loadAiPluginsButton");
const validationPlanSummary = document.querySelector("#validationPlanSummary");
const aiPluginSummary = document.querySelector("#aiPluginSummary");
const depthWorkflowSummary = document.querySelector("#depthWorkflowSummary");
const depthProbeSummary = document.querySelector("#depthProbeSummary");
const depthDemoSummary = document.querySelector("#depthDemoSummary");
const historySearch = document.querySelector("#historySearch");
const historyList = document.querySelector("#historyList");
const refreshHistoryButton = document.querySelector("#refreshHistoryButton");
const exportHistoryLink = document.querySelector("#exportHistoryLink");
const reviewSearch = document.querySelector("#reviewSearch");
const reviewSummaryGrid = document.querySelector("#reviewSummaryGrid");
const reviewList = document.querySelector("#reviewList");
const refreshReviewButton = document.querySelector("#refreshReviewButton");
const exportReviewLink = document.querySelector("#exportReviewLink");
const exportReviewTruthLink = document.querySelector("#exportReviewTruthLink");
const usageSummaryGrid = document.querySelector("#usageSummaryGrid");
const usageEndpointList = document.querySelector("#usageEndpointList");
const refreshUsageButton = document.querySelector("#refreshUsageButton");
const exportUsageLink = document.querySelector("#exportUsageLink");

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
  if (!key) {
    return "--";
  }
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
  updateWorkflowAutoSummary();
  if (state.lastResult) {
    renderResult(state.lastResult, { keepView: true });
  } else {
    loadHistory();
  }
  if (state.depthStatus) {
    renderDepthStatus(state.depthStatus);
  }
  if (state.depthProbe) {
    renderDepthProbe(state.depthProbe);
  }
  if (state.depthWorkflow) {
    renderDepthWorkflow(state.depthWorkflow);
  }
  if (state.validationPlan) {
    renderValidationPlan(state.validationPlan);
  }
  if (state.aiPlugins) {
    renderAiPlugins(state.aiPlugins);
  }
  if (state.reviewSamples) {
    renderReviewSamples(state.reviewSamples);
  }
  if (state.usageSummary) {
    renderUsageSummary(state.usageSummary);
  }
  if (state.lastDepthDemo) {
    renderDepthDemo(state.lastDepthDemo);
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

function formatKg(value) {
  return Number.isFinite(Number(value)) ? `${Number(value).toFixed(3)} kg` : "--";
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
    "part_category",
    "package_hint",
    "material_hint",
    "actual_weight_kg",
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
    await loadUsageSummary();
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
  industrySummary.innerHTML = "";
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

  const hasTopImage = Boolean(data.top_view?.annotated_image_url);
  copyJsonButton.disabled = false;
  adjustTopButton.disabled = !hasTopImage;
  showTopViewButton.disabled = !hasTopImage;
  showSideViewButton.disabled = !data.side_view?.annotated_image_url;
  showTopViewButton.classList.toggle("is-active", state.activeView === "top");
  showSideViewButton.classList.toggle("is-active", state.activeView === "side");
  renderStageImage();
  renderSideSummary(data);
  renderIndustrySummary(data.industry_profile, { autoLoadWorkflow: !options.keepView });
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

function renderIndustrySummary(profile, options = {}) {
  industrySummary.innerHTML = "";
  if (!profile) {
    return;
  }
  syncWorkflowControls(profile);
  if (options.autoLoadWorkflow) {
    void loadDepthWorkflow({ auto: true });
  }
  const card = document.createElement("div");
  card.className = "industry-card";
  appendSummaryCell(card, t("packageClass"), labelFrom(packageClassLabels, profile.package_class));
  appendSummaryCell(card, t("materialClass"), labelFrom(materialClassLabels, profile.material_class) || "--");
  appendSummaryCell(card, t("captureMode"), labelFrom(captureModeLabels, profile.recommended_capture_mode));
  appendSummaryCell(card, t("chargeableWeight"), formatKg(profile.chargeable_weight_kg));
  industrySummary.appendChild(card);
}

function appendSummaryCell(parent, label, value) {
  const item = document.createElement("div");
  const labelEl = document.createElement("span");
  const valueEl = document.createElement("strong");
  labelEl.textContent = label;
  valueEl.textContent = value || "--";
  item.append(labelEl, valueEl);
  parent.appendChild(item);
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

async function loadDepthStatus() {
  if (!depthStatusGrid) {
    return;
  }
  const response = await fetch("/api/depth/status");
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  state.depthStatus = data;
  renderDepthStatus(data);
}

function renderDepthStatus(data) {
  depthStatusGrid.innerHTML = "";
  const openNiReady = Boolean(data.openni2?.openni_dll_found && data.openni2?.orbbec_driver_found);
  const pyorbbecReady = Boolean(data.pyorbbecsdk_available);
  const driverReady = Boolean(data.windows_driver?.found);
  const inventory = data.camera_inventory || {};
  const configuredCount = Number(inventory.configured_camera_count || 0);
  const targetCount = Number(inventory.target_camera_count || configuredCount || 1);
  const detectedCount = Number(inventory.openni_probe?.device_count || 0);
  const missingThreeView = inventory.missing_three_view_roles || [];
  appendDepthPill(depthStatusGrid, t("depthBackend"), data.recommended_backend || "--", Boolean(data.ready_for_hardware_trial));
  appendDepthPill(depthStatusGrid, t("depthOpenNi"), openNiReady ? t("ready") : t("missing"), openNiReady);
  appendDepthPill(depthStatusGrid, t("depthPyorbbec"), pyorbbecReady ? t("installed") : t("unavailable"), pyorbbecReady);
  appendDepthPill(depthStatusGrid, t("depthDriver"), driverReady ? t("installed") : t("missing"), driverReady);
  appendDepthPill(depthStatusGrid, t("depthConfiguredCameras"), `${configuredCount}/${targetCount}`, configuredCount > 0);
  appendDepthPill(depthStatusGrid, t("depthDetectedDevices"), String(detectedCount), detectedCount > 0);
  appendDepthPill(
    depthStatusGrid,
    t("depthThreeView"),
    missingThreeView.length ? `${t("missing")}: ${missingThreeView.join(", ")}` : t("ready"),
    missingThreeView.length === 0,
  );
}

function appendDepthPill(parent, label, value, isReady) {
  const pill = document.createElement("div");
  pill.className = `depth-pill ${isReady ? "is-ready" : "is-warning"}`;
  const labelEl = document.createElement("span");
  const valueEl = document.createElement("strong");
  labelEl.textContent = label;
  valueEl.textContent = value || "--";
  pill.append(labelEl, valueEl);
  parent.appendChild(pill);
}

async function probeDepthCapture() {
  probeDepthCaptureButton.disabled = true;
  try {
    const response = await fetch("/api/depth/capture/probe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backend: "auto" }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.depthProbe = data;
    renderDepthProbe(data);
  } catch (error) {
    depthProbeSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    depthProbeSummary.appendChild(item);
  } finally {
    probeDepthCaptureButton.disabled = false;
  }
}

function renderDepthProbe(data) {
  depthProbeSummary.innerHTML = "";
  const card = document.createElement("div");
  card.className = "depth-demo-card depth-probe-card";
  appendSummaryCell(card, t("captureProbe"), data.ready ? t("ready") : t("missing"));
  appendSummaryCell(card, t("captureStatus"), labelFrom(probeStatusLabels, data.status));
  appendSummaryCell(card, t("selectedBackend"), data.backend_selected || "--");
  depthProbeSummary.appendChild(card);

  const actionKeys = data.next_action_keys || [];
  const actions = actionKeys.length ? actionKeys : data.next_actions || [];
  actions.forEach((action, index) => {
    const item = document.createElement("div");
    item.className = "recommendation";
    const fallback = data.next_actions?.[index] || action;
    item.textContent = `${t("nextAction")}: ${labelFrom(probeActionLabels, action) || fallback}`;
    depthProbeSummary.appendChild(item);
  });
}

async function loadDepthWorkflow(options = {}) {
  loadDepthWorkflowButton.disabled = true;
  try {
    const params = buildWorkflowParams();
    const response = await fetch(`/api/depth/workflow-guide?${params.toString()}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.depthWorkflow = data;
    renderDepthWorkflow(data);
    updateWorkflowAutoSummary(data.recommended_workflow);
  } catch (error) {
    depthWorkflowSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    depthWorkflowSummary.appendChild(item);
  } finally {
    loadDepthWorkflowButton.disabled = false;
  }
}

function buildWorkflowParams() {
  const params = new URLSearchParams({
    package_class: workflowPackageSelect?.value || "standard_carton",
    camera_count: workflowCameraCountSelect?.value || "1",
  });
  if (workflowMaterialSelect?.value) {
    params.set("material_class", workflowMaterialSelect.value);
  }
  return params;
}

function syncWorkflowControls(profile) {
  if (!profile || !workflowPackageSelect || !workflowMaterialSelect) {
    return;
  }
  if (profile.package_class && optionExists(workflowPackageSelect, profile.package_class)) {
    workflowPackageSelect.value = profile.package_class;
  }
  const materialClass = profile.material_class || "";
  if (optionExists(workflowMaterialSelect, materialClass)) {
    workflowMaterialSelect.value = materialClass;
  }
  if (workflowCameraCountSelect) {
    workflowCameraCountSelect.value = autoCameraCountForProfile(profile);
  }
  updateWorkflowAutoSummary(profile);
}

function optionExists(select, value) {
  return Array.from(select.options).some((option) => option.value === value);
}

function autoCameraCountForProfile(profile) {
  return ["long_part", "bulky_irregular"].includes(profile.package_class) ? "2" : "1";
}

function updateWorkflowAutoSummary(source) {
  if (!workflowAutoSummary) {
    return;
  }
  const packageClass = source?.package_class || workflowPackageSelect?.value || "standard_carton";
  const materialClass = source?.material_class || workflowMaterialSelect?.value || "";
  const cameraCount = source?.camera_count || workflowCameraCountSelect?.value || "1";
  const parts = [
    labelFrom(scenarioLabels, packageClass),
    materialClass ? labelFrom(materialClassLabels, materialClass) : t("autoMaterial"),
    `${cameraCount} x Astra Pro`,
  ];
  workflowAutoSummary.textContent = parts.join(" / ");
}

function renderDepthWorkflow(data) {
  depthWorkflowSummary.innerHTML = "";
  const workflow = data.recommended_workflow || {};
  const guide = data.guide || {};

  const lead = document.createElement("div");
  lead.className = "depth-workflow-card";
  appendSummaryCell(lead, t("workflowGuide"), labelFrom(scenarioLabels, workflow.package_class) || "--");
  appendSummaryCell(lead, t("cameraCount"), String(workflow.camera_count || "--"));
  appendSummaryCell(lead, t("motherboard"), workflow.upgrade_advice?.motherboard_required_now ? t("required") : t("notRequired"));
  depthWorkflowSummary.appendChild(lead);

  const readiness = document.createElement("div");
  readiness.className = "depth-workflow-card";
  appendSummaryCell(readiness, t("arrivalKit"), firstLabels(workflow.readiness_item_ids, workflowLabels, 4));
  const cameraPose = workflow.package_class ? labelFrom(cameraPoseLabels, workflow.package_class) : workflow.camera_pose;
  appendSummaryCell(readiness, t("captureMode"), cameraPose || "--");
  appendSummaryCell(readiness, t("nextAction"), firstLabels(guide.first_hour_steps, workflowLabels, 3));
  depthWorkflowSummary.appendChild(readiness);

  const steps = document.createElement("div");
  steps.className = "depth-workflow-card";
  appendSummaryCell(steps, t("captureSteps"), firstLabels(workflow.capture_step_ids, workflowLabels, 5));
  appendSummaryCell(steps, t("materialClass"), labelFrom(scenarioLabels, workflow.material_class) || "--");
  appendSummaryCell(steps, t("nextAction"), firstLabels(workflow.upgrade_advice?.try_before_upgrade, workflowLabels, 4));
  depthWorkflowSummary.appendChild(steps);
}

function firstLabels(ids = [], dictionary = null, limit = 4) {
  const values = ids.slice(0, limit).map((id) => (dictionary ? labelFrom(dictionary, id) : id.replaceAll("_", " ")));
  return values.length ? values.join(" / ") : "--";
}

async function loadValidationPlan() {
  loadValidationPlanButton.disabled = true;
  try {
    const response = await fetch("/api/validation/trial-plan");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.validationPlan = data;
    renderValidationPlan(data);
  } catch (error) {
    validationPlanSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    validationPlanSummary.appendChild(item);
  } finally {
    loadValidationPlanButton.disabled = false;
  }
}

function renderValidationPlan(data) {
  validationPlanSummary.innerHTML = "";
  const lead = document.createElement("div");
  lead.className = "validation-plan-card is-total";
  appendSummaryCell(lead, t("validationPlan"), t("totalSamples"));
  appendSummaryCell(lead, t("totalSamples"), String(data.minimum_total_samples || "--"));
  validationPlanSummary.appendChild(lead);

  for (const scenario of data.scenarios || []) {
    const card = document.createElement("div");
    card.className = "validation-plan-card";
    appendSummaryCell(card, labelFrom(scenarioLabels, scenario.id), scenario.required_capture_mode || "--");
    appendSummaryCell(card, t("minSamples"), String(scenario.minimum_samples || "--"));
    appendSummaryCell(card, t("tolerance"), formatTolerance(scenario));
    validationPlanSummary.appendChild(card);
  }

  for (const material of data.material_scenarios || []) {
    const card = document.createElement("div");
    card.className = "validation-plan-card is-material";
    appendSummaryCell(card, labelFrom(scenarioLabels, material.id), material.risk_level || "--");
    appendSummaryCell(card, t("minSamples"), String(material.minimum_samples || "--"));
    appendSummaryCell(card, t("captureMode"), labelFrom(flagLabels, material.flags?.[0]) || "--");
    validationPlanSummary.appendChild(card);
  }
}

function formatTolerance(scenario) {
  if (!scenario?.abs_tolerance_mm || !scenario?.relative_tolerance_pct) {
    return scenario?.acceptance || "--";
  }
  return t("toleranceTemplate")
    .replace("{mm}", String(scenario.abs_tolerance_mm))
    .replace("{pct}", String(scenario.relative_tolerance_pct));
}

async function loadAiPlugins() {
  loadAiPluginsButton.disabled = true;
  try {
    const response = await fetch("/api/ai/plugins");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.aiPlugins = data;
    renderAiPlugins(data);
  } catch (error) {
    aiPluginSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    aiPluginSummary.appendChild(item);
  } finally {
    loadAiPluginsButton.disabled = false;
  }
}

function renderAiPlugins(data) {
  aiPluginSummary.innerHTML = "";
  const summary = data.summary || {};
  const lead = document.createElement("div");
  lead.className = "depth-probe-card";
  appendSummaryCell(lead, t("aiPluginStatus"), data.status || "--");
  appendSummaryCell(lead, t("aiPluginReady"), String(summary.ready_count || 0));
  appendSummaryCell(lead, t("aiPluginAttention"), String(summary.attention_count || 0));
  aiPluginSummary.appendChild(lead);

  const policy = document.createElement("div");
  policy.className = "depth-probe-card";
  appendSummaryCell(policy, t("aiPluginPolicy"), data.base_package_policy?.heavy_models_bundled ? t("required") : t("notRequired"));
  appendSummaryCell(policy, t("captureMode"), firstLabels(data.fallback_chain || [], null, 4));
  aiPluginSummary.appendChild(policy);

  const plugins = data.plugins || [];
  if (!plugins.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = t("aiPluginNoPlugins");
    aiPluginSummary.appendChild(empty);
    return;
  }

  for (const plugin of plugins.slice(0, 4)) {
    const card = document.createElement("div");
    card.className = "depth-probe-card";
    appendSummaryCell(card, plugin.name || plugin.id, plugin.status || "--");
    appendSummaryCell(card, t("captureMode"), firstLabels(plugin.capabilities || [], null, 3));
    appendSummaryCell(card, t("nextAction"), firstLabels((plugin.issues || []).map((item) => item.code), null, 2));
    aiPluginSummary.appendChild(card);
  }
}

async function runDepthDemo() {
  runDepthDemoButton.disabled = true;
  try {
    const response = await fetch("/api/depth/demo-object");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.lastDepthDemo = data;
    renderDepthDemo(data);
    await loadUsageSummary();
  } catch (error) {
    depthDemoSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    depthDemoSummary.appendChild(item);
  } finally {
    runDepthDemoButton.disabled = false;
  }
}

async function saveDepthDemo() {
  saveDepthDemoButton.disabled = true;
  try {
    const response = await fetch("/api/depth/demo-object/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentTraceabilityPayload()),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    state.lastDepthDemo = data;
    renderDepthDemo(data);
    renderResult(data);
    await loadHistory();
    await loadUsageSummary();
  } catch (error) {
    depthDemoSummary.innerHTML = "";
    const item = document.createElement("div");
    item.className = "recommendation";
    item.textContent = String(error.message || error);
    depthDemoSummary.appendChild(item);
  } finally {
    saveDepthDemoButton.disabled = false;
  }
}

function currentTraceabilityPayload() {
  return {
    order_id: orderIdInput.value || `DEPTH-${Date.now().toString().slice(-6)}`,
    barcode_text: barcodeTextInput.value || orderIdInput.value || "",
    part_category: form.elements.part_category?.value || "",
    package_hint: form.elements.package_hint?.value || "irregular",
    material_hint: form.elements.material_hint?.value || "",
    actual_weight_kg: Number(form.elements.actual_weight_kg?.value || 0) || null,
  };
}

function renderDepthDemo(data) {
  depthDemoSummary.innerHTML = "";
  const card = document.createElement("div");
  card.className = "depth-demo-card";
  appendSummaryCell(card, t("depthDemo"), data.sample?.name || t("demoObject"));
  appendSummaryCell(card, t("length"), formatMm(data.dimensions?.length_mm));
  appendSummaryCell(card, t("height"), formatMm(data.dimensions?.height_mm));
  appendSummaryCell(card, t("history"), data.history_saved ? t("savedToHistory") : "--");
  depthDemoSummary.appendChild(card);
}

async function loadUsageSummary() {
  if (!usageSummaryGrid || !usageEndpointList) {
    return;
  }
  const response = await fetch("/api/usage/summary");
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  state.usageSummary = data;
  renderUsageSummary(data);
}

function renderUsageSummary(data) {
  usageSummaryGrid.innerHTML = "";
  usageEndpointList.innerHTML = "";
  const today = new Date().toISOString().slice(0, 10);
  const todayRow = (data.by_day || []).find((item) => item.day === today);
  const successRate = data.total_calls
    ? `${Math.round((Number(data.successful_calls || 0) / Number(data.total_calls)) * 100)}%`
    : "--";

  appendUsageCard(t("todayMeasurements"), todayRow?.measurement_calls || 0, today);
  appendUsageCard(t("measurementCalls"), data.measurement_calls || 0, t("totalCalls"));
  appendUsageCard(t("failedCalls"), data.failed_calls || 0, t("successRate") + ` ${successRate}`);
  appendUsageCard(t("lastEvent"), data.last_event_at ? formatDate(data.last_event_at) : "--", t("endpointBreakdown"));

  if (exportUsageLink) {
    exportUsageLink.href = "/api/usage/export.csv?limit=1000";
  }

  const endpoints = data.by_endpoint || [];
  if (!endpoints.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = t("noUsage");
    usageEndpointList.appendChild(empty);
    return;
  }

  for (const item of endpoints.slice(0, 8)) {
    const row = document.createElement("div");
    row.className = "usage-row";
    appendSummaryCell(row, item.endpoint, `${item.call_count || 0} | ${item.method || "GET"}`);
    appendSummaryCell(row, t("measurementCalls"), String(item.measurement_calls || 0));
    appendSummaryCell(row, t("failedCalls"), String(item.failed_calls || 0));
    usageEndpointList.appendChild(row);
  }
}

function appendUsageCard(label, value, sub) {
  const card = document.createElement("div");
  card.className = "usage-card";
  const labelEl = document.createElement("span");
  const valueEl = document.createElement("strong");
  const subEl = document.createElement("small");
  labelEl.textContent = label;
  valueEl.textContent = String(value ?? "--");
  subEl.textContent = sub || "";
  card.append(labelEl, valueEl, subEl);
  usageSummaryGrid.appendChild(card);
}

async function loadReviewSamples() {
  if (!reviewSummaryGrid || !reviewList) {
    return;
  }
  const params = new URLSearchParams();
  if (reviewSearch.value.trim()) {
    params.set("order_id", reviewSearch.value.trim());
  }
  params.set("limit", "50");
  updateReviewExportLink(params);
  const response = await fetch(`/api/review/samples?${params}`);
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  state.reviewSamples = data;
  renderReviewSamples(data);
}

function updateReviewExportLink(params) {
  if (!exportReviewLink) {
    return;
  }
  const exportParams = new URLSearchParams(params);
  exportParams.set("limit", "500");
  exportReviewLink.href = `/api/review/export.csv?${exportParams}`;
  if (exportReviewTruthLink) {
    exportReviewTruthLink.href = `/api/review/truth-template.csv?${exportParams}`;
  }
}

function renderReviewSamples(data) {
  reviewSummaryGrid.innerHTML = "";
  reviewList.innerHTML = "";
  const items = data.items || [];
  const summary = data.summary || {};
  const byPriority = summary.by_priority || {};
  const highCount = Number(byPriority.critical || 0) + Number(byPriority.high || 0);
  const topReason = summary.top_reasons?.[0]?.reason || "--";
  appendReviewCard(t("reviewSamples"), summary.total_review_samples || 0, t("review"));
  appendReviewCard(t("highPriority"), highCount, "critical + high");
  appendReviewCard(t("topReviewReason"), topReason, t("suggestedAction"));

  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = t("noReview");
    reviewList.appendChild(empty);
    return;
  }

  for (const item of items) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = `history-row review-priority-${item.priority || "medium"}`;
    row.addEventListener("click", () => openHistoryItem(item.measurement_id));
    appendHistoryCell(row, item.order_id || item.barcode_text || item.measurement_id, formatDate(item.created_at), true);
    appendHistoryCell(row, item.priority || "medium", `${Math.round((item.confidence || 0) * 100)}% | ${item.status || "--"}`, false);
    appendHistoryCell(row, labelFrom(packageClassLabels, item.package_class), labelFrom(materialClassLabels, item.material_class), false);
    appendHistoryCell(row, (item.review_reasons || []).slice(0, 3).join(" | "), t("topReviewReason"), false);
    appendHistoryCell(row, item.suggested_action || "--", t("suggestedAction"), false);
    reviewList.appendChild(row);
  }
}

function appendReviewCard(label, value, sub) {
  const card = document.createElement("div");
  card.className = "usage-card";
  const labelEl = document.createElement("span");
  const valueEl = document.createElement("strong");
  const subEl = document.createElement("small");
  labelEl.textContent = label;
  valueEl.textContent = String(value ?? "--");
  subEl.textContent = sub || "";
  card.append(labelEl, valueEl, subEl);
  reviewSummaryGrid.appendChild(card);
}

async function loadHistory() {
  const params = new URLSearchParams();
  if (historySearch.value.trim()) {
    params.set("order_id", historySearch.value.trim());
  }
  params.set("limit", "30");
  updateHistoryExportLink(params);
  const response = await fetch(`/api/history?${params}`);
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  renderHistory(data.items || []);
}

function updateHistoryExportLink(params) {
  if (!exportHistoryLink) {
    return;
  }
  const exportParams = new URLSearchParams(params);
  exportParams.set("limit", "500");
  exportHistoryLink.href = `/api/history/export.csv?${exportParams}`;
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
    appendHistoryCell(row, item.status, historyStatusMeta(item), false);
    appendHistoryCell(row, labelFrom(packageClassLabels, item.package_class), labelFrom(captureModeLabels, item.recommended_capture_mode), false);
    appendHistoryCell(row, formatMm(item.length_mm), t("length"), false);
    appendHistoryCell(row, formatMm(item.width_mm), t("width"), false);
    appendHistoryCell(row, formatMm(item.height_mm), t("height"), false);
    appendHistoryCell(row, formatKg(item.chargeable_weight_kg), t("chargeableWeight"), false);
    historyList.appendChild(row);
  }
}

function historyStatusMeta(item) {
  const confidence = `${Math.round((item.confidence || 0) * 100)}%`;
  const method = item.measurement_method ? item.measurement_method.replaceAll("_", " ") : "";
  return method ? `${confidence} | ${method}` : confidence;
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
refreshReviewButton.addEventListener("click", loadReviewSamples);
refreshUsageButton.addEventListener("click", loadUsageSummary);
refreshDepthStatusButton.addEventListener("click", loadDepthStatus);
probeDepthCaptureButton.addEventListener("click", probeDepthCapture);
loadDepthWorkflowButton.addEventListener("click", loadDepthWorkflow);
for (const select of [workflowPackageSelect, workflowMaterialSelect, workflowCameraCountSelect]) {
  select.addEventListener("change", () => {
    updateWorkflowAutoSummary();
    if (state.depthWorkflow) {
      loadDepthWorkflow();
    }
  });
}
loadValidationPlanButton.addEventListener("click", loadValidationPlan);
loadAiPluginsButton.addEventListener("click", loadAiPlugins);
runDepthDemoButton.addEventListener("click", runDepthDemo);
saveDepthDemoButton.addEventListener("click", saveDepthDemo);
historySearch.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    loadHistory();
  }
});
reviewSearch.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    loadReviewSamples();
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
loadDepthStatus();
loadHistory();
loadReviewSamples();
loadUsageSummary();
