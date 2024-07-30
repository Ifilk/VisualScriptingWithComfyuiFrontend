import {app} from "../../../scripts/app.js";
import {ComfyWidgets} from "../../../scripts/widgets.js";
import {api} from "../../../scripts/api.js";

app.registerExtension({
    name: "base.LoadMat",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        console.log(nodeData)
        if (nodeData?.input?.required?.file?.[1]?.file_upload === true) {
            nodeData.input.required.upload = ["FILEUPLOAD"];
        }
    },
});
