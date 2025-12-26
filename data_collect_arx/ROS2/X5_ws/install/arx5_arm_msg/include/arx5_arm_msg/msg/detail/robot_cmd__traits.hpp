// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arx5_arm_msg:msg/RobotCmd.idl
// generated code does not contain a copyright notice

#ifndef ARX5_ARM_MSG__MSG__DETAIL__ROBOT_CMD__TRAITS_HPP_
#define ARX5_ARM_MSG__MSG__DETAIL__ROBOT_CMD__TRAITS_HPP_

#include "arx5_arm_msg/msg/detail/robot_cmd__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arx5_arm_msg::msg::RobotCmd>()
{
  return "arx5_arm_msg::msg::RobotCmd";
}

template<>
inline const char * name<arx5_arm_msg::msg::RobotCmd>()
{
  return "arx5_arm_msg/msg/RobotCmd";
}

template<>
struct has_fixed_size<arx5_arm_msg::msg::RobotCmd>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<arx5_arm_msg::msg::RobotCmd>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<arx5_arm_msg::msg::RobotCmd>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ARX5_ARM_MSG__MSG__DETAIL__ROBOT_CMD__TRAITS_HPP_
