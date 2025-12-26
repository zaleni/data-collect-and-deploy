import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "MVVM Demo"

    RowLayout {
        anchors.fill: parent
        spacing: 5

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 10

            // 图像显示区域
            RowLayout {
                spacing: 5
                Layout.alignment: Qt.AlignTop

                Column {
                    Image {
                        id: image1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "image://liveimage/wrist"
                        fillMode: Image.PreserveAspectFit

                        Connections {
                            target: viewModel
                            function onImageUpdated() {
                                image1.source = "image://liveimage/wrist?t=" + Date.now();
                            }
                        }
                    }
                    Text {
                        text: "wristImage"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        width: image1.width  // 与图片同宽
                    }
                }
                
                Column {
                    Image {
                        id: image2
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        source: "image://liveimage/front"
                        fillMode: Image.PreserveAspectFit

                        Connections {
                            target: viewModel
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

            // 输入区域
            RowLayout {
                spacing: 10
                TextField {
                    id: inputField
                    placeholderText: "请输入内容"
                    onTextChanged: viewModel.validateInput(text)
                }

                Button {
                    text: "确认"
                    enabled: viewModel.inputValid && !viewModel.confirmed
                    // enabled: true
                    onClicked: viewModel.confirm()
                }
            }

            // 控制按钮
            RowLayout {
                spacing: 10
                Button {
                    text: "开始录制"
                    enabled: viewModel.confirmed && !viewModel.isSaving
                    onClicked: viewModel.start()
                }

                Button {
                    text: "停止录制"
                    enabled: viewModel.confirmed && viewModel.isSaving
                    onClicked: viewModel.stop()
                }

                Button {
                    text: "重播数据"
                    enabled: viewModel.confirmed && !viewModel.isSaving && viewModel.selectedTask
                    onClicked: viewModel.replay()
                }

                Button {
                    text: "Live模式"
                    enabled: viewModel.confirmed && !viewModel.isSaving && !viewModel.isLiving
                    onClicked: viewModel.live()
                }
            }

            // 数据展示
            GridLayout {
                columns: 2
                rowSpacing: 5
                columnSpacing: 10

                Text {
                    text: "X:"
                    font.pointSize: 14
                }
                Text {
                    text: viewModel.x
                    color: viewModel.xColor
                    font.pointSize: 14
                }
                Text {
                    text: "Y:"
                    font.pointSize: 14
                }
                Text {
                    text: viewModel.y
                    color: viewModel.yColor
                    font.pointSize: 14
                }
                Text {
                    text: "Z:"
                }
                Text {
                    text: viewModel.z
                    color: viewModel.zColor
                    font.pointSize: 14
                }
                Text {
                    text: "RX:"
                }
                Text {
                    text: viewModel.rx
                }
                Text {
                    text: "RY:"
                }
                Text {
                    text: viewModel.ry
                }
                Text {
                    text: "RZ:"
                }
                Text {
                    text: viewModel.rz
                }
                Text {
                    text: "Gripper:"
                }
                Text {
                    text: viewModel.gripper
                }
            }
        }

        ScrollView {
            // Layout.fillWidth: true
            Layout.preferredWidth: 200
            Layout.fillHeight: true

            ListView {
                id: listView
                anchors.fill: parent
                spacing: 2
                model: viewModel.savedTasks  // 绑定到ViewModel的列表

                delegate: Rectangle {
                    width: listView.width
                    height: 40
                    color: index == viewModel.selectedTaskIndex ? "#e0f0ff" : "transparent"

                    Text {
                        text: modelData
                        anchors.verticalCenter: parent.verticalCenter
                        leftPadding: 10
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: viewModel.handleSelection(index)
                    }
                }
            }
        }
    }

    // ColumnLayout {
    //     anchors.fill: parent
    //     spacing: 10

    //     // ListView {
    //     //     id: taskListView
    //     //     anchors.fill: parent
    //     //     model: viewModel.savedTasks.length  // 绑定到Python端的savedTasks属性
    //     //     currentIndex: -1    // 初始化无选中状态

    //     //     delegate: Rectangle {
    //     //         width: parent.width
    //     //         height: 40
    //     //         color: taskListView.currentIndex === index ? "lightblue" : "white"

    //     //         Text {
    //     //             text: modelData  // 显示字符串内容
    //     //             anchors.verticalCenter: parent.verticalCenter
    //     //             // padding: 5
    //     //         }

    //     //         MouseArea {
    //     //             anchors.fill: parent
    //     //             onClicked: {
    //     //                 taskListView.currentIndex = index
    //     //                 viewModel.handleSelection(index, modelData)  // 传递索引和内容
    //     //             }
    //     //         }
    //     //     }

    //     //     // 可选：滚动条
    //     //     ScrollBar.vertical: ScrollBar {}
    //     // }

        

    //     // // 状态栏
    //     // Rectangle {
    //     //     Layout.fillWidth: true
    //     //     height: 30
    //     //     color: "lightgray"

    //     //     RowLayout {
    //     //         anchors.fill: parent
    //     //         spacing: 10

    //     //         Rectangle {
    //     //             width: 20
    //     //             height: 20
    //     //             radius: 10
    //     //             color: viewModel.statusColor
    //     //         }

    //     //         Text {
    //     //             text: viewModel.status
    //     //             font.pixelSize: 16
    //     //         }
    //     //     }
    //     // }

    // }
}
