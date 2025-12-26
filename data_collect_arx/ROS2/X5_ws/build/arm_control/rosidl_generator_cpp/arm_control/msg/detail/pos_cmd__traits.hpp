// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from arm_control:msg/PosCmd.idl
// generated code does not contain a copyright notice

#ifndef ARM_CONTROL__MSG__DETAIL__POS_CMD__TRAITS_HPP_
#define ARM_CONTROL__MSG__DETAIL__POS_CMD__TRAITS_HPP_

#include "arm_control/msg/detail/pos_cmd__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<arm_control::msg::PosCmd>()
{
  return "arm_control::msg::PosCmd";
}

template<>
inline const char * name<arm_control::msg::PosCmd>()
{
  return "arm_control/msg/PosCmd";
}

template<>
struct has_fixed_size<arm_control::msg::PosCmd>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<arm_control::msg::PosCmd>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<arm_control::msg::PosCmd>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ARM_CONTROL__MSG__DETAIL__POS_CMD__TRAITS_HPP_
