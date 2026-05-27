# PackVision AI Plugin Directory

This folder is intentionally lightweight. Do not commit model weights into the base package.

Supported plugin layout:

```text
models/
  packvision-yolo/
    plugin.json
    weights/
      model.onnx       # optional, ignored by default
  segmentation/
    plugin.json
  depth-prior/
    plugin.json
```

`plugin.json` example:

```json
{
  "id": "packvision-yolo-carton",
  "name": "PackVision carton detector",
  "version": "0.1.0",
  "enabled": true,
  "engine": "onnxruntime_cpu",
  "capabilities": ["box_detection", "oriented_box_detection"],
  "runtime_dependencies": ["onnxruntime"],
  "model_files": [
    { "path": "weights/model.onnx", "required": true }
  ],
  "priority": "assist",
  "description": "Optional detector for cartons and long parts. Depth/manual fallback remains required."
}
```

Runtime discovery:

- Source checkout: `D:\Documents\包装尺寸检测\models`
- User install: `%LOCALAPPDATA%\PackVision\models`
- Override: `PACKVISION_AI_MODEL_ROOT`

The base EXE must continue to work when this folder has no plugins.
