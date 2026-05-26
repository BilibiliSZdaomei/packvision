const translations = {
  zh: {
    localLab: "本地仓库测量台",
    measure: "测量",
    depth: "深度",
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
    partCategory: "备件类型",
    packageHint: "包装类型",
    materialHint: "材质/表面",
    autoPackage: "自动判断",
    autoMaterial: "自动/普通",
    carton: "标准纸箱",
    longPart: "长条件",
    irregular: "异形件",
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
    industrySummary: "行业摘要",
    packageClass: "包装分类",
    materialClass: "材质风险",
    captureMode: "推荐采集",
    chargeableWeight: "计费重量",
    exportCsv: "导出 CSV",
    depthTitle: "Astra Pro 深度相机工作区",
    refreshDepth: "刷新状态",
    probeDepthCapture: "采集探测",
    validationPlan: "验收计划",
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
    partCategory: "Part category",
    packageHint: "Package type",
    materialHint: "Material",
    autoPackage: "Auto",
    autoMaterial: "Auto / normal",
    carton: "Carton",
    longPart: "Long part",
    irregular: "Irregular",
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
    industrySummary: "Industry summary",
    packageClass: "Package class",
    materialClass: "Material risk",
    captureMode: "Capture mode",
    chargeableWeight: "Chargeable weight",
    exportCsv: "Export CSV",
    depthTitle: "Astra Pro depth camera workspace",
    refreshDepth: "Refresh status",
    probeDepthCapture: "Probe capture",
    validationPlan: "Trial plan",
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
    partCategory: "Тип деталі",
    packageHint: "Тип пакування",
    materialHint: "Матеріал",
    autoPackage: "Авто",
    autoMaterial: "Авто / звичайний",
    carton: "Коробка",
    longPart: "Довга деталь",
    irregular: "Нерівна",
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
    industrySummary: "Галузевий підсумок",
    packageClass: "Клас пакування",
    materialClass: "Ризик матеріалу",
    captureMode: "Режим зйомки",
    chargeableWeight: "Платна вага",
    exportCsv: "Експорт CSV",
    depthTitle: "Робоча зона Astra Pro",
    refreshDepth: "Оновити статус",
    probeDepthCapture: "Перевірити збір",
    validationPlan: "План приймання",
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
    depth_outliers_trimmed: "深度离群点已裁剪",
    point_cloud_extent_trimmed: "点云范围已裁剪",
    small_object_mask: "目标掩膜偏小",
    reflective_depth_noise_risk: "反光材质深度噪声风险",
    transparent_depth_dropout_risk: "透明材质深度丢失风险",
    dark_surface_depth_dropout_risk: "深黑材质深度丢失风险",
    deformable_shape_drift_risk: "软材形变风险",
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
    depth_outliers_trimmed: "Depth outliers trimmed",
    point_cloud_extent_trimmed: "Point-cloud extent trimmed",
    small_object_mask: "Small object mask",
    reflective_depth_noise_risk: "Reflective depth-noise risk",
    transparent_depth_dropout_risk: "Transparent depth-dropout risk",
    dark_surface_depth_dropout_risk: "Dark-surface dropout risk",
    deformable_shape_drift_risk: "Deformable-shape drift risk",
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
    depth_outliers_trimmed: "Викиди глибини обрізано",
    point_cloud_extent_trimmed: "Хмару точок обрізано",
    small_object_mask: "Мала маска об'єкта",
    reflective_depth_noise_risk: "Ризик шуму від відблиску",
    transparent_depth_dropout_risk: "Ризик втрати глибини прозорого",
    dark_surface_depth_dropout_risk: "Ризик втрати темної поверхні",
    deformable_shape_drift_risk: "Ризик деформації форми",
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

const localeMap = { zh: "zh-CN", en: "en-US", uk: "uk-UA" };

const state = {
  lang: localStorage.getItem("packvision.lang") || "zh",
  theme: localStorage.getItem("packvision.theme") || "light",
  lastResult: null,
  depthStatus: null,
  depthProbe: null,
  validationPlan: null,
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
const loadValidationPlanButton = document.querySelector("#loadValidationPlanButton");
const runDepthDemoButton = document.querySelector("#runDepthDemoButton");
const saveDepthDemoButton = document.querySelector("#saveDepthDemoButton");
const validationPlanSummary = document.querySelector("#validationPlanSummary");
const depthProbeSummary = document.querySelector("#depthProbeSummary");
const depthDemoSummary = document.querySelector("#depthDemoSummary");
const historySearch = document.querySelector("#historySearch");
const historyList = document.querySelector("#historyList");
const refreshHistoryButton = document.querySelector("#refreshHistoryButton");
const exportHistoryLink = document.querySelector("#exportHistoryLink");

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
  if (state.validationPlan) {
    renderValidationPlan(state.validationPlan);
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
  renderIndustrySummary(data.industry_profile);
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

function renderIndustrySummary(profile) {
  industrySummary.innerHTML = "";
  if (!profile) {
    return;
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
  appendDepthPill(depthStatusGrid, t("depthBackend"), data.recommended_backend || "--", Boolean(data.ready_for_hardware_trial));
  appendDepthPill(depthStatusGrid, t("depthOpenNi"), openNiReady ? t("ready") : t("missing"), openNiReady);
  appendDepthPill(depthStatusGrid, t("depthPyorbbec"), pyorbbecReady ? t("installed") : t("unavailable"), pyorbbecReady);
  appendDepthPill(depthStatusGrid, t("depthDriver"), driverReady ? t("installed") : t("missing"), driverReady);
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
refreshDepthStatusButton.addEventListener("click", loadDepthStatus);
probeDepthCaptureButton.addEventListener("click", probeDepthCapture);
loadValidationPlanButton.addEventListener("click", loadValidationPlan);
runDepthDemoButton.addEventListener("click", runDepthDemo);
saveDepthDemoButton.addEventListener("click", saveDepthDemo);
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
loadDepthStatus();
loadHistory();
