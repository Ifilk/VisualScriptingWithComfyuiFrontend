import {app} from "/scripts/app.js";

app.registerExtension({
        name: "base.LoadMat",
        async beforeRegisterNodeDef(nodeType, nodeData, app) {
            if (nodeData?.input?.required?.file?.[1]?.file_upload === true) {
                nodeData.input.required.upload = ["FILEUPLOAD"];
            }
        },
        getCustomWidgets() {
            return {
                FILEUPLOAD(node, inputName, inputData, app) {
                    console.log(node.widgets)
                    const imageWidget = node.widgets.find((w) => w.name === (inputData[1]?.widget ?? "image"));
                    let uploadWidget;
                    console.log(imageWidget)

                    async function uploadFile(file, updateNode, pasted = false) {
                        try {
                            // Wrap file in formdata so it includes filename
                            const body = new FormData();
                            body.append("file", file);
                            if (pasted) body.append("subfolder", "pasted");
                            const resp = await api.fetchApi("/upload/file", {
                                method: "POST",
                                body,
                            });

                            if (resp.status === 200) {
                                // const data = await resp.json();
                                // // Add the file to the dropdown list and update the widget value
                                // let path = data.name;
                                // if (data.subfolder) path = data.subfolder + "/" + path;
                                //
                                // if (!imageWidget.options.values.includes(path)) {
                                // 	imageWidget.options.values.push(path);
                                // }
                                //
                                // if (updateNode) {
                                // 	showImage(path);
                                // 	imageWidget.value = path;
                                // }
                            } else {
                                alert(resp.status + " - " + resp.statusText);
                            }
                        } catch (error) {
                            alert(error);
                        }
                    }

                    console.log('right------------------')
                    const fileInput = document.createElement("input");
                    Object.assign(fileInput, {
                        type: "file",
                        accept: ".npy",
                        style: "display: none",
                        onchange: async () => {
                            if (fileInput.files.length) {
                                await uploadFile(fileInput.files[0], true);
                            }
                        },
                    });
                    document.body.append(fileInput);

                    // Create the button widget for selecting the files
                    uploadWidget = node.addWidget("button", inputName, "image", () => {
                        fileInput.click();
                    });
                    uploadWidget.label = "choose file to upload";
                    uploadWidget.serialize = false;

                    // Add handler to check if an image is being dragged over our node
                    node.onDragOver = function (e) {
                        if (e.dataTransfer && e.dataTransfer.items) {
                            const image = [...e.dataTransfer.items].find((f) => f.kind === "file");
                            return !!image;
                        }
                        return false;
                    };

                    // On drop upload files
                    node.onDragDrop = function (e) {
                        console.log("onDragDrop called");
                        let handled = false;
                        for (const file of e.dataTransfer.files) {
                            console.log(file.type)
                            // if (file.type.startsWith("image/")) {
                            // 	uploadFile(file, !handled); // Dont await these, any order is fine, only update on first one
                            // 	handled = true;
                            // }
                        }
                        return handled;
                    };

                    // node.pasteFile = function(file) {
                    // 	if (file.type.startsWith("image/")) {
                    // 		const is_pasted = (file.name === "image.png") &&
                    // 						  (file.lastModified - Date.now() < 2000);
                    // 		uploadFile(file, true, is_pasted);
                    // 		return true;
                    // 	}
                    // 	return false;
                    // }

                    return {widget: uploadWidget};
                }
            }
        }
    }
)

