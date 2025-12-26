import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    width: 800
    height: 700
    minimumWidth: 600
    minimumHeight: 400
    visible: true
    title: "智能指令控制系统"

    ColumnLayout {
        anchors.centerIn: parent  // 整体布局居中
        anchors.margins: 20
        spacing: 20

        // 1. 录音控制区域
        GroupBox {
            title: "录音控制"
            Layout.fillWidth: true

            RowLayout {
                width: parent.width
                spacing: 20
                Layout.alignment: Qt.AlignHCenter

                Button {
                    id: recordButton
                    text: backend.isRecording ? "停止录音" : "开始录音"
                    onClicked: {
                        if (backend.isRecording) {
                            backend.stopRecording()
                        } else {
                            backend.startRecording()
                        }
                    }
                }

                Label {
                    text: backend.isRecording ? "● 正在录音..." : "○ 准备录音"
                    color: backend.isRecording ? "red" : "green"
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // 2. 模式选择区域
        GroupBox {
            title: "mode"
            Layout.fillWidth: true

            RowLayout {
                width: parent.width
                spacing: 20
                Layout.alignment: Qt.AlignHCenter

                Button {
                    id: modeButton
                    text: backend.currentMode === "vla" ? "返回" : "VLA模式"
                    onClicked: {
                        backend.set_mode()
                    }
                }
            }
        }

        // 3. 指令显示区域和第一个图片
        RowLayout {
            Layout.fillWidth: true
            spacing: 20
            Layout.alignment: Qt.AlignHCenter  // 水平居中对齐

            GroupBox {
                title: "当前指令"
                Layout.preferredWidth: 400

                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 20
                    rowSpacing: 10
                    Layout.alignment: Qt.AlignHCenter

                    Label {
                        text: "VLM指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    Rectangle {
                        width: 200
                        height: 40
                        border.color: "gray"
                        radius: 5

                        Text {
                            anchors.fill: parent
                            anchors.margins: 5
                            text: backend.vlmInstruction
                            wrapMode: Text.Wrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Label {
                        text: "VLA指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    Rectangle {
                        width: 200
                        height: 40
                        border.color: "gray"
                        radius: 5

                        Text {
                            anchors.fill: parent
                            anchors.margins: 5
                            text: backend.vlaInstruction
                            wrapMode: Text.Wrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Label {
                        text: "LLM指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    Rectangle {
                        width: 200
                        height: 40
                        border.color: "gray"
                        radius: 5

                        Text {
                            anchors.fill: parent
                            anchors.margins: 5
                            text: backend.llmInstruction
                            wrapMode: Text.Wrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Label {
                        text: "franka指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    Rectangle {
                        width: 200
                        height: 40
                        border.color: "gray"
                        radius: 5

                        Text {
                            anchors.fill: parent
                            anchors.margins: 5
                            text: backend.frankaInstruction
                            wrapMode: Text.Wrap
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }

            Column {
                Image {
                    id: image1
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    source: "image://liveimage/wrist"
                    fillMode: Image.PreserveAspectFit
                    Layout.maximumWidth: 150  // 减小最大宽度
                    Layout.maximumHeight: 150  // 减小最大高度

                    Connections {
                        target: backend
                        function onImageUpdated() {
                            image1.source = "image://liveimage/wrist?t=" + Date.now();
                        }
                    }
                }
                Text {
                    text: "wristImage"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    width: image1.width
                }
            }
        }

        // 4. 指令输入区域和第二个图片
        RowLayout {
            Layout.fillWidth: true
            spacing: 20
            Layout.alignment: Qt.AlignHCenter  // 水平居中对齐

            GroupBox {
                title: "指令设置"
                Layout.preferredWidth: 400

                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 20
                    rowSpacing: 10
                    Layout.alignment: Qt.AlignHCenter

                    Label {
                        text: "VLM指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    TextField {
                        id: vlmInput
                        Layout.preferredWidth: 200
                        placeholderText: "输入新的VLM指令..."
                        selectByMouse: true
                    }

                    Label {
                        text: "VLA指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    TextField {
                        id: vlaInput
                        Layout.preferredWidth: 200
                        placeholderText: "输入新的VLA指令..."
                        selectByMouse: true
                    }

                    Label {
                        text: "LLM指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    TextField {
                        id: llmInput
                        Layout.preferredWidth: 200
                        placeholderText: "输入新的LLM指令..."
                        selectByMouse: true
                    }

                    Label {
                        text: "franka指令："
                        font.bold: true
                        Layout.alignment: Qt.AlignRight
                        verticalAlignment: Text.AlignVCenter
                    }

                    TextField {
                        id: frankaInput
                        Layout.preferredWidth: 200
                        placeholderText: "输入新的franka指令..."
                        selectByMouse: true
                    }
                }
            }

            Column {
                Image {
                    id: image2
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    source: "image://liveimage/front"
                    fillMode: Image.PreserveAspectFit
                    Layout.maximumWidth: 150  // 减小最大宽度
                    Layout.maximumHeight: 150  // 减小最大高度

                    Connections {
                        target: backend
                        function onImageUpdated() {
                            image2.source = "image://liveimage/front?t=" + Date.now();
                        }
                    }
                }
                Text {
                    text: "FrontImage"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    width: image2.width
                }
            }
        }

        // 5. 控制按钮区域
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 20

            Button {
                text: "设置VLM指令"
                onClicked: {
                    if (vlmInput.text) {
                        backend.set_vlm(vlmInput.text)
                        vlmInput.clear()
                    }
                }
            }

            Button {
                text: "设置VLA指令"
                onClicked: {
                    if (vlaInput.text) {
                        backend.set_vla(vlaInput.text)
                        vlaInput.clear()
                    }
                }
            }

            Button {
                text: "设置LLM指令"
                onClicked: {
                    if (llmInput.text) {
                        backend.set_llm(llmInput.text)
                        llmInput.clear()
                    }
                }
            }

            Button {
                text: "设置franka指令"
                onClicked: {
                    if (frankaInput.text) {
                        backend.set_franka(frankaInput.text)
                        frankaInput.clear()
                    }
                }
            }

            Button {
                text: backend.armRunning ? "停止机械臂" : "启动机械臂"
                onClicked: backend.setArmRunning(!backend.armRunning)
            }
        }

        // 6. 状态栏
        Label {
            Layout.alignment: Qt.AlignHCenter
            text: {
                if (backend.armRunning && backend.isRecording) {
                    return "状态：机械臂运行中 | 正在录音"
                } else if (backend.armRunning) {
                    return "状态：机械臂运行中"
                } else if (backend.isRecording) {
                    return "状态：正在录音"
                } else {
                    return "状态：准备就绪"
                }
            }
            font.bold: true
            color: "steelblue"
        }
    }
}    