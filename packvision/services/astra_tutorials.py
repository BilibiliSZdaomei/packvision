from __future__ import annotations

from typing import Any


ASTRA_TUTORIAL_SOURCES: list[dict[str, str]] = [
    {
        "id": "ros2_readme",
        "path_hint": r"D:\app\orbbec-astra-pro\sdk\ros2_openni\ros2_astra_camera\README.MD",
        "packvision_use": "ROS2 services, launch parameters, multi-camera startup, calibration URL contract.",
    },
    {
        "id": "astra_pro_launch",
        "path_hint": r"D:\app\orbbec-astra-pro\sdk\ros2_openni\ros2_astra_camera\astra_camera\launch\astra_pro.launch.xml",
        "packvision_use": "Astra Pro default stream, point cloud, D2C, UVC and device_num parameters.",
    },
    {
        "id": "multi_astra_launch",
        "path_hint": r"D:\app\orbbec-astra-pro\sdk\ros2_openni\ros2_astra_camera\astra_camera\launch\multi_astra.launch.xml",
        "packvision_use": "Two or more Astra cameras require device_num, serial separation and cleanup_shm_node.",
    },
    {
        "id": "ros1_barcode_qr",
        "path_hint": r"D:\app\orbbec-astra-pro\vendor\ROS1系列教程\2、Opencv应用\2、Opencv应用.md",
        "packvision_use": "Barcode and QR detection idea maps to PackVision order-number upload/scanner endpoints.",
    },
    {
        "id": "ros1_point_cloud",
        "path_hint": r"D:\app\orbbec-astra-pro\vendor\ROS1系列教程\5、数据转换和点云\5、数据转换和点云.md",
        "packvision_use": "Point-cloud export is useful for engineering validation, not warehouse daily operation.",
    },
]


ASTRA_ROS2_CONTROL_CATALOG: list[dict[str, Any]] = [
    {
        "group": "camera_identity_and_intrinsics",
        "warehouse_visible": False,
        "controls": [
            {
                "id": "get_camera_info",
                "service": "/camera/get_camera_info",
                "service_type": "astra_camera_msgs/srv/GetCameraInfo",
                "mode": "read",
                "packvision_mapping": "/api/depth/camera-info/normalize",
                "why_it_matters": "Use vendor intrinsics so workers do not enter focal length or aperture.",
            },
            {
                "id": "get_camera_params",
                "service": "/camera/get_camera_params",
                "service_type": "astra_camera_msgs/srv/GetCameraParams",
                "mode": "read",
                "packvision_mapping": "depth vendor profile and hardware acceptance",
                "why_it_matters": "Records factory calibration and stream parameters for traceability.",
            },
            {
                "id": "get_device_info",
                "service": "/camera/get_device_info",
                "service_type": "astra_camera_msgs/srv/GetDeviceInfo",
                "mode": "read",
                "packvision_mapping": "depth camera inventory serial_hint",
                "why_it_matters": "Serial numbers are the reliable way to assign top/front/left cameras.",
            },
            {
                "id": "get_sdk_version",
                "service": "/camera/get_sdk_version",
                "service_type": "astra_camera_msgs/srv/GetString",
                "mode": "read",
                "packvision_mapping": "driver install report",
                "why_it_matters": "Keeps field reports tied to the exact vendor SDK.",
            },
        ],
    },
    {
        "group": "exposure_gain_white_balance",
        "warehouse_visible": False,
        "controls": [
            {
                "id": "set_ir_auto_exposure",
                "service": "/camera/set_ir_auto_exposure",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "engineer-only low-light troubleshooting",
                "why_it_matters": "IR exposure changes depth stability for dark, reflective or distant parts.",
            },
            {
                "id": "set_ir_exposure",
                "service": "/camera/set_ir_exposure",
                "service_type": "astra_camera_msgs/srv/SetInt32",
                "mode": "write",
                "safe_default": None,
                "packvision_mapping": "engineer-only fixed exposure test",
                "why_it_matters": "Manual IR exposure is useful when auto exposure flickers under warehouse lighting.",
            },
            {
                "id": "get_ir_exposure",
                "service": "/camera/get_ir_exposure",
                "service_type": "astra_camera_msgs/srv/GetInt32",
                "mode": "read",
                "packvision_mapping": "depth quality incident log",
                "why_it_matters": "Capture exposure values when measurements fail so the cause is traceable.",
            },
            {
                "id": "set_color_auto_exposure",
                "service": "/camera/set_color_auto_exposure",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "photo/order-image quality troubleshooting",
                "why_it_matters": "Color stream affects barcode images, operator previews and D2C overlays.",
            },
            {
                "id": "set_color_exposure",
                "service": "/camera/set_color_exposure",
                "service_type": "astra_camera_msgs/srv/SetInt32",
                "mode": "write",
                "safe_default": None,
                "packvision_mapping": "engineer-only preview tuning",
                "why_it_matters": "Fixed RGB exposure can improve repeatable validation photos.",
            },
            {
                "id": "set_color_auto_white_balance",
                "service": "/camera/set_color_auto_white_balance",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "barcode and preview color stability",
                "why_it_matters": "White balance drift can hurt color-based segmentation references.",
            },
            {
                "id": "set_ir_gain",
                "service": "/camera/set_ir_gain",
                "service_type": "astra_camera_msgs/srv/SetInt32",
                "mode": "write",
                "safe_default": None,
                "packvision_mapping": "engineer-only depth dropout troubleshooting",
                "why_it_matters": "Gain changes noise and valid-pixel ratio on difficult materials.",
            },
            {
                "id": "get_ir_gain",
                "service": "/camera/get_ir_gain",
                "service_type": "astra_camera_msgs/srv/GetInt32",
                "mode": "read",
                "packvision_mapping": "depth quality incident log",
                "why_it_matters": "Record gain with quality flags for later accuracy reports.",
            },
        ],
    },
    {
        "group": "orientation_streams_and_emitters",
        "warehouse_visible": False,
        "controls": [
            {
                "id": "set_depth_mirror",
                "service": "/camera/set_depth_mirror",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": False,
                "packvision_mapping": "camera role mounting profile",
                "why_it_matters": "Side or inverted mounting must not silently flip measurement axes.",
            },
            {
                "id": "set_color_mirror",
                "service": "/camera/set_color_mirror",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": False,
                "packvision_mapping": "operator preview orientation",
                "why_it_matters": "Keeps preview, barcode overlay and manual ROI adjustment aligned.",
            },
            {
                "id": "set_laser_enable",
                "service": "/camera/set_laser_enable",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "hardware acceptance only",
                "why_it_matters": "Emitter state directly affects depth availability.",
            },
            {
                "id": "toggle_depth",
                "service": "/camera/toggle_depth",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "stream-health recovery",
                "why_it_matters": "Lets engineers restart depth stream without restarting the whole app.",
            },
            {
                "id": "toggle_color",
                "service": "/camera/toggle_color",
                "service_type": "std_srvs/srv/SetBool",
                "mode": "write",
                "safe_default": True,
                "packvision_mapping": "preview and barcode stream recovery",
                "why_it_matters": "Useful when RGB stream is UVC and reconnects separately.",
            },
        ],
    },
]


ASTRA_ROS2_LAUNCH_PARAMETERS: list[dict[str, Any]] = [
    {
        "name": "device_num",
        "recommended_value": "number of enabled depth cameras",
        "packvision_mapping": "target_camera_count",
        "why_it_matters": "The vendor driver uses this when launching multiple cameras.",
    },
    {
        "name": "serial_number",
        "recommended_value": "set per camera once known",
        "packvision_mapping": "cameras[].serial_hint",
        "why_it_matters": "Serial number is the stable way to bind top/front/left roles.",
    },
    {
        "name": "connection_delay",
        "recommended_value": 100,
        "packvision_mapping": "cameras[].ros2_profile.connection_delay_ms",
        "why_it_matters": "Gives devices time to reopen after reconnects or multi-camera startup.",
    },
    {
        "name": "enable_point_cloud",
        "recommended_value": True,
        "packvision_mapping": "engineering validation mode",
        "why_it_matters": "Point cloud is useful for tuning and proof, while warehouse measurement can stay API-only.",
    },
    {
        "name": "enable_colored_point_cloud",
        "recommended_value": False,
        "packvision_mapping": "disabled by default for light runtime",
        "why_it_matters": "RGB point clouds cost bandwidth; enable only for D2C validation.",
    },
    {
        "name": "depth_registration",
        "recommended_value": False,
        "packvision_mapping": "turn on when RGB-depth overlay or colored point cloud is required",
        "why_it_matters": "Depth-to-color alignment helps overlays but may add compute cost and constraints.",
    },
    {
        "name": "color_depth_synchronization",
        "recommended_value": True,
        "packvision_mapping": "traceable capture mode",
        "why_it_matters": "Keeps RGB preview/order image and depth measurement from drifting in time.",
    },
    {
        "name": "use_uvc_camera",
        "recommended_value": True,
        "packvision_mapping": "Astra Pro RGB stream profile",
        "why_it_matters": "Astra Pro launch file defaults RGB through UVC in the reviewed ROS2 package.",
    },
    {
        "name": "ir_info_url",
        "recommended_value": "file:///path/to/depth_camera.yaml",
        "packvision_mapping": "/api/depth/camera-info/normalize stream=depth",
        "why_it_matters": "Factory or calibration YAML removes manual intrinsic entry.",
    },
    {
        "name": "color_info_url",
        "recommended_value": "file:///path/to/rgb_camera.yaml",
        "packvision_mapping": "/api/depth/camera-info/normalize stream=color",
        "why_it_matters": "Needed for reliable RGB-depth overlays and operator preview checks.",
    },
]


ASTRA_MULTI_CAMERA_PLAYBOOK: dict[str, Any] = {
    "target_topology": ["top", "front", "left_or_right"],
    "vendor_commands": {
        "list_devices": "ros2 run astra_camera list_devices_node",
        "cleanup_shared_memory": "ros2 run astra_camera cleanup_shm_node",
        "single_astra_pro": "ros2 launch astra_camera astra_pro.launch.xml",
        "multi_astra": "ros2 launch astra_camera multi_astra.launch.xml",
    },
    "setup_order": [
        "First validate one camera in OrbbecViewer and PackVision capture probe.",
        "Record serial number, physical role and mount pose.",
        "Repeat for each camera before running multi_astra.launch.xml.",
        "Set device_num to the enabled camera count.",
        "Run cleanup_shm_node after failed ROS2 startups before retrying.",
        "Use PackVision /api/depth/cameras to confirm role mapping and missing views.",
    ],
    "packvision_contract": [
        "Every camera keeps a camera_id, role, backend, serial_hint and ros2_profile.",
        "Measurement APIs accept camera_id or role and do not change when cameras are added.",
        "Fusion stays conservative_max to avoid under-reporting chargeable shipping dimensions.",
    ],
}


ASTRA_CALIBRATION_CONTRACT: dict[str, Any] = {
    "warehouse_worker_policy": "Workers never enter focal length, aperture or intrinsics manually.",
    "priority": [
        "Read /camera/depth/camera_info from the running driver.",
        "Import ir_camera or rgb_camera calibration YAML from vendor/ROS tools.",
        "Use PackVision FOV estimate only as an engineering fallback before final validation.",
    ],
    "expected_camera_names": {
        "depth_or_ir": "ir_camera",
        "color_or_rgb": "rgb_camera",
    },
    "api_mapping": {
        "normalize": "/api/depth/camera-info/normalize",
        "measure_roi": "/api/depth/measure-roi",
        "measure_object": "/api/depth/measure-object",
    },
    "when_to_recalibrate": [
        "Repeated truth-check error after mount is fixed.",
        "Camera was dropped, lens moved or housing changed.",
        "RGB-depth overlay is required and D2C alignment is visibly wrong.",
    ],
}


ASTRA_TUTORIAL_GAP_ANALYSIS: list[dict[str, Any]] = [
    {
        "topic": "ROS2 exposure, gain, mirror, laser and stream services",
        "status": "integrated_as_control_catalog",
        "why": "These are engineer-only controls for light, orientation and stream failures.",
    },
    {
        "topic": "Multi-camera device_num, serial binding and cleanup_shm_node",
        "status": "integrated_as_multi_camera_playbook",
        "why": "This is required before top/front/left three-view validation.",
    },
    {
        "topic": "ir_info_url and color_info_url calibration YAML",
        "status": "integrated_as_calibration_contract",
        "why": "It preserves the no-manual-intrinsics warehouse workflow.",
    },
    {
        "topic": "Colored point cloud and D2C alignment",
        "status": "integrated_as_engineering_mode",
        "why": "Useful for validation and demos; disabled by default for lightweight warehouse runtime.",
    },
    {
        "topic": "ROS1 QR/barcode tutorial",
        "status": "already_covered_by_packvision_order_decode",
        "why": "PackVision already has scanner/manual/upload order-number flows.",
    },
    {
        "topic": "Microphone tutorial",
        "status": "intentionally_excluded",
        "why": "It does not affect packaging dimension measurement.",
    },
]


def build_astra_tutorial_playbook() -> dict[str, Any]:
    return {
        "status": "reviewed_and_project_mapped",
        "worker_policy": "automatic measurement first; engineer controls stay hidden from warehouse operators",
        "sources_reviewed": ASTRA_TUTORIAL_SOURCES,
        "control_catalog": ASTRA_ROS2_CONTROL_CATALOG,
        "launch_parameter_catalog": ASTRA_ROS2_LAUNCH_PARAMETERS,
        "multi_camera_playbook": ASTRA_MULTI_CAMERA_PLAYBOOK,
        "calibration_contract": ASTRA_CALIBRATION_CONTRACT,
        "gap_analysis": ASTRA_TUTORIAL_GAP_ANALYSIS,
    }


def build_astra_ros2_camera_profile(
    camera_id: str,
    role: str,
    *,
    device_num: int = 1,
    serial_number: str | None = None,
) -> dict[str, Any]:
    namespace = "camera" if device_num <= 1 else f"{role}_camera"
    return {
        "driver_family": "ros2_astra_camera",
        "camera_id": camera_id,
        "role": role,
        "namespace": namespace,
        "launch_file": "astra_pro.launch.xml" if device_num <= 1 else "multi_astra.launch.xml",
        "device_num": max(1, int(device_num)),
        "serial_number": serial_number,
        "connection_delay_ms": 100,
        "streams": {
            "enable_color": True,
            "enable_depth": True,
            "enable_ir": False,
            "color_depth_synchronization": True,
        },
        "point_cloud": {
            "enable_point_cloud": True,
            "enable_colored_point_cloud": False,
            "depth_registration": False,
            "engineering_only": True,
        },
        "calibration_urls": {
            "ir_info_url": "",
            "color_info_url": "",
            "expected_depth_camera_name": "ir_camera",
            "expected_color_camera_name": "rgb_camera",
        },
        "uvc": {
            "use_uvc_camera": True,
            "uvc_product_id": "",
            "uvc_retry_count": 100,
        },
        "operator_policy": {
            "manual_intrinsics_allowed": False,
            "exposure_controls_visible_to_worker": False,
            "measurement_mode": "auto",
        },
    }
