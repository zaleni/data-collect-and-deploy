// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from arx5_arm_msg:msg/RobotStatus.idl
// generated code does not contain a copyright notice
#include "arx5_arm_msg/msg/detail/robot_status__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "arx5_arm_msg/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "arx5_arm_msg/msg/detail/robot_status__struct.h"
#include "arx5_arm_msg/msg/detail/robot_status__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_arx5_arm_msg
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_arx5_arm_msg
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_arx5_arm_msg
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _RobotStatus__ros_msg_type = arx5_arm_msg__msg__RobotStatus;

static bool _RobotStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _RobotStatus__ros_msg_type * ros_message = static_cast<const _RobotStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->header, cdr))
    {
      return false;
    }
  }

  // Field name: end_pos
  {
    size_t size = 6;
    auto array_ptr = ros_message->end_pos;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: joint_pos
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_pos;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: joint_vel
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_vel;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: joint_cur
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_cur;
    cdr.serializeArray(array_ptr, size);
  }

  return true;
}

static bool _RobotStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _RobotStatus__ros_msg_type * ros_message = static_cast<_RobotStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->header))
    {
      return false;
    }
  }

  // Field name: end_pos
  {
    size_t size = 6;
    auto array_ptr = ros_message->end_pos;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: joint_pos
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_pos;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: joint_vel
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_vel;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: joint_cur
  {
    size_t size = 7;
    auto array_ptr = ros_message->joint_cur;
    cdr.deserializeArray(array_ptr, size);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arx5_arm_msg
size_t get_serialized_size_arx5_arm_msg__msg__RobotStatus(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RobotStatus__ros_msg_type * ros_message = static_cast<const _RobotStatus__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name header

  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);
  // field.name end_pos
  {
    size_t array_size = 6;
    auto array_ptr = ros_message->end_pos;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name joint_pos
  {
    size_t array_size = 7;
    auto array_ptr = ros_message->joint_pos;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name joint_vel
  {
    size_t array_size = 7;
    auto array_ptr = ros_message->joint_vel;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name joint_cur
  {
    size_t array_size = 7;
    auto array_ptr = ros_message->joint_cur;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _RobotStatus__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_arx5_arm_msg__msg__RobotStatus(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arx5_arm_msg
size_t max_serialized_size_arx5_arm_msg__msg__RobotStatus(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;

  // member: header
  {
    size_t array_size = 1;


    for (size_t index = 0; index < array_size; ++index) {
      current_alignment +=
        max_serialized_size_std_msgs__msg__Header(
        full_bounded, current_alignment);
    }
  }
  // member: end_pos
  {
    size_t array_size = 6;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: joint_pos
  {
    size_t array_size = 7;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: joint_vel
  {
    size_t array_size = 7;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: joint_cur
  {
    size_t array_size = 7;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  return current_alignment - initial_alignment;
}

static size_t _RobotStatus__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_arx5_arm_msg__msg__RobotStatus(
    full_bounded, 0);
}


static message_type_support_callbacks_t __callbacks_RobotStatus = {
  "arx5_arm_msg::msg",
  "RobotStatus",
  _RobotStatus__cdr_serialize,
  _RobotStatus__cdr_deserialize,
  _RobotStatus__get_serialized_size,
  _RobotStatus__max_serialized_size
};

static rosidl_message_type_support_t _RobotStatus__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_RobotStatus,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, arx5_arm_msg, msg, RobotStatus)() {
  return &_RobotStatus__type_support;
}

#if defined(__cplusplus)
}
#endif
