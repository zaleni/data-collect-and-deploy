// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from arm_control:msg/PosCmd.idl
// generated code does not contain a copyright notice
#include "arm_control/msg/detail/pos_cmd__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "arm_control/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "arm_control/msg/detail/pos_cmd__struct.h"
#include "arm_control/msg/detail/pos_cmd__functions.h"
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


// forward declare type support functions


using _PosCmd__ros_msg_type = arm_control__msg__PosCmd;

static bool _PosCmd__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _PosCmd__ros_msg_type * ros_message = static_cast<const _PosCmd__ros_msg_type *>(untyped_ros_message);
  // Field name: x
  {
    cdr << ros_message->x;
  }

  // Field name: y
  {
    cdr << ros_message->y;
  }

  // Field name: z
  {
    cdr << ros_message->z;
  }

  // Field name: roll
  {
    cdr << ros_message->roll;
  }

  // Field name: pitch
  {
    cdr << ros_message->pitch;
  }

  // Field name: yaw
  {
    cdr << ros_message->yaw;
  }

  // Field name: gripper
  {
    cdr << ros_message->gripper;
  }

  // Field name: quater_x
  {
    cdr << ros_message->quater_x;
  }

  // Field name: quater_y
  {
    cdr << ros_message->quater_y;
  }

  // Field name: quater_z
  {
    cdr << ros_message->quater_z;
  }

  // Field name: quater_w
  {
    cdr << ros_message->quater_w;
  }

  // Field name: chx
  {
    cdr << ros_message->chx;
  }

  // Field name: chy
  {
    cdr << ros_message->chy;
  }

  // Field name: chz
  {
    cdr << ros_message->chz;
  }

  // Field name: vel_l
  {
    cdr << ros_message->vel_l;
  }

  // Field name: vel_r
  {
    cdr << ros_message->vel_r;
  }

  // Field name: height
  {
    cdr << ros_message->height;
  }

  // Field name: head_pit
  {
    cdr << ros_message->head_pit;
  }

  // Field name: head_yaw
  {
    cdr << ros_message->head_yaw;
  }

  // Field name: temp_float_data
  {
    size_t size = 6;
    auto array_ptr = ros_message->temp_float_data;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: temp_int_data
  {
    size_t size = 6;
    auto array_ptr = ros_message->temp_int_data;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: mode1
  {
    cdr << ros_message->mode1;
  }

  // Field name: mode2
  {
    cdr << ros_message->mode2;
  }

  // Field name: time_count
  {
    cdr << ros_message->time_count;
  }

  return true;
}

static bool _PosCmd__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _PosCmd__ros_msg_type * ros_message = static_cast<_PosCmd__ros_msg_type *>(untyped_ros_message);
  // Field name: x
  {
    cdr >> ros_message->x;
  }

  // Field name: y
  {
    cdr >> ros_message->y;
  }

  // Field name: z
  {
    cdr >> ros_message->z;
  }

  // Field name: roll
  {
    cdr >> ros_message->roll;
  }

  // Field name: pitch
  {
    cdr >> ros_message->pitch;
  }

  // Field name: yaw
  {
    cdr >> ros_message->yaw;
  }

  // Field name: gripper
  {
    cdr >> ros_message->gripper;
  }

  // Field name: quater_x
  {
    cdr >> ros_message->quater_x;
  }

  // Field name: quater_y
  {
    cdr >> ros_message->quater_y;
  }

  // Field name: quater_z
  {
    cdr >> ros_message->quater_z;
  }

  // Field name: quater_w
  {
    cdr >> ros_message->quater_w;
  }

  // Field name: chx
  {
    cdr >> ros_message->chx;
  }

  // Field name: chy
  {
    cdr >> ros_message->chy;
  }

  // Field name: chz
  {
    cdr >> ros_message->chz;
  }

  // Field name: vel_l
  {
    cdr >> ros_message->vel_l;
  }

  // Field name: vel_r
  {
    cdr >> ros_message->vel_r;
  }

  // Field name: height
  {
    cdr >> ros_message->height;
  }

  // Field name: head_pit
  {
    cdr >> ros_message->head_pit;
  }

  // Field name: head_yaw
  {
    cdr >> ros_message->head_yaw;
  }

  // Field name: temp_float_data
  {
    size_t size = 6;
    auto array_ptr = ros_message->temp_float_data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: temp_int_data
  {
    size_t size = 6;
    auto array_ptr = ros_message->temp_int_data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: mode1
  {
    cdr >> ros_message->mode1;
  }

  // Field name: mode2
  {
    cdr >> ros_message->mode2;
  }

  // Field name: time_count
  {
    cdr >> ros_message->time_count;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arm_control
size_t get_serialized_size_arm_control__msg__PosCmd(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _PosCmd__ros_msg_type * ros_message = static_cast<const _PosCmd__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name x
  {
    size_t item_size = sizeof(ros_message->x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name y
  {
    size_t item_size = sizeof(ros_message->y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name z
  {
    size_t item_size = sizeof(ros_message->z);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name roll
  {
    size_t item_size = sizeof(ros_message->roll);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name pitch
  {
    size_t item_size = sizeof(ros_message->pitch);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name yaw
  {
    size_t item_size = sizeof(ros_message->yaw);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name gripper
  {
    size_t item_size = sizeof(ros_message->gripper);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name quater_x
  {
    size_t item_size = sizeof(ros_message->quater_x);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name quater_y
  {
    size_t item_size = sizeof(ros_message->quater_y);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name quater_z
  {
    size_t item_size = sizeof(ros_message->quater_z);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name quater_w
  {
    size_t item_size = sizeof(ros_message->quater_w);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name chx
  {
    size_t item_size = sizeof(ros_message->chx);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name chy
  {
    size_t item_size = sizeof(ros_message->chy);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name chz
  {
    size_t item_size = sizeof(ros_message->chz);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name vel_l
  {
    size_t item_size = sizeof(ros_message->vel_l);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name vel_r
  {
    size_t item_size = sizeof(ros_message->vel_r);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name height
  {
    size_t item_size = sizeof(ros_message->height);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name head_pit
  {
    size_t item_size = sizeof(ros_message->head_pit);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name head_yaw
  {
    size_t item_size = sizeof(ros_message->head_yaw);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name temp_float_data
  {
    size_t array_size = 6;
    auto array_ptr = ros_message->temp_float_data;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name temp_int_data
  {
    size_t array_size = 6;
    auto array_ptr = ros_message->temp_int_data;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name mode1
  {
    size_t item_size = sizeof(ros_message->mode1);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name mode2
  {
    size_t item_size = sizeof(ros_message->mode2);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name time_count
  {
    size_t item_size = sizeof(ros_message->time_count);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _PosCmd__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_arm_control__msg__PosCmd(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_arm_control
size_t max_serialized_size_arm_control__msg__PosCmd(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;

  // member: x
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: y
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: z
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: roll
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: pitch
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: yaw
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: gripper
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: quater_x
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: quater_y
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: quater_z
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: quater_w
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: chx
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: chy
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: chz
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: vel_l
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: vel_r
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: height
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: head_pit
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: head_yaw
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: temp_float_data
  {
    size_t array_size = 6;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: temp_int_data
  {
    size_t array_size = 6;

    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: mode1
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: mode2
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: time_count
  {
    size_t array_size = 1;

    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  return current_alignment - initial_alignment;
}

static size_t _PosCmd__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_arm_control__msg__PosCmd(
    full_bounded, 0);
}


static message_type_support_callbacks_t __callbacks_PosCmd = {
  "arm_control::msg",
  "PosCmd",
  _PosCmd__cdr_serialize,
  _PosCmd__cdr_deserialize,
  _PosCmd__get_serialized_size,
  _PosCmd__max_serialized_size
};

static rosidl_message_type_support_t _PosCmd__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_PosCmd,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, arm_control, msg, PosCmd)() {
  return &_PosCmd__type_support;
}

#if defined(__cplusplus)
}
#endif
