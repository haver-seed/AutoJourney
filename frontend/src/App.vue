<template>
  <Home />
</template>

<script setup>
import Home from './views/Home.vue'
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display',
    system-ui, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  background-color: #ffffff;
  color: #1d1d1f;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.47;
}

/* ---- Apple-style Element Plus overrides ---- */

/* Primary button: charcoal pill */
.el-button--primary {
  background-color: #1d1d1f !important;
  border-color: #1d1d1f !important;
  border-radius: 9999px !important;
  font-weight: 400 !important;
  color: #fff !important;
}
.el-button--primary:hover,
.el-button--primary:focus {
  background-color: #424245 !important;
  border-color: #424245 !important;
}
.el-button--primary:active {
  background-color: #0a0a0a !important;
  border-color: #0a0a0a !important;
}
.el-button--primary.is-plain {
  background-color: rgba(29, 29, 31, 0.06) !important;
  color: #1d1d1f !important;
  border-color: transparent !important;
}
.el-button--primary.is-plain:hover,
.el-button--primary.is-plain:focus {
  background-color: rgba(29, 29, 31, 0.12) !important;
  color: #424245 !important;
  border-color: transparent !important;
}

/* Success button: green pill */
.el-button--success {
  background-color: #16a34a !important;
  border-color: #16a34a !important;
  border-radius: 9999px !important;
  color: #fff !important;
}
.el-button--success:hover,
.el-button--success:focus {
  background-color: #15803d !important;
  border-color: #15803d !important;
}
.el-button--success.is-plain {
  background-color: rgba(22, 163, 74, 0.08) !important;
  color: #16a34a !important;
  border-color: transparent !important;
}

/* Radio */
.el-radio__input.is-checked .el-radio__inner {
  border-color: #1d1d1f !important;
  background-color: #1d1d1f !important;
}
.el-radio__input.is-checked + .el-radio__label {
  color: #1d1d1f !important;
}

/* Slider */
.el-slider__button {
  border-color: #1d1d1f !important;
}
.el-slider__bar {
  background-color: #1d1d1f !important;
}

/* Danger button: keep visible */
.el-button--danger.is-circle {
  color: #ff3b30 !important;
  background: transparent !important;
  border-color: #ff3b30 !important;
}
.el-button--danger.is-circle:hover {
  background: #ff3b30 !important;
  color: #fff !important;
}

/* Circle buttons (move up/down) */
.el-button.is-circle {
  background: #f5f5f7 !important;
  border-color: #d2d2d7 !important;
  color: #1d1d1f !important;
}
.el-button.is-circle:hover {
  background: #e8e8ed !important;
  border-color: #86868b !important;
}

/* Input */
.el-input__wrapper {
  border-radius: 8px !important;
}
.el-textarea__inner {
  border-radius: 8px !important;
}

/* Autocomplete dropdown */
.el-autocomplete-suggestion li {
  padding: 10px 16px !important;
  font-size: 15px !important;
}

/* Tag */
.el-tag {
  border-radius: 9999px !important;
}

/* Date picker */
.el-date-editor {
  width: 100% !important;
}

/* Input number */
.el-input-number--small {
  width: 90px !important;
}
.el-input-number .el-input__wrapper {
  border-radius: 8px !important;
}
.el-input-number__decrease,
.el-input-number__increase {
  border-radius: 8px !important;
  background: #f5f5f7 !important;
  border-color: #d2d2d7 !important;
  color: #1d1d1f !important;
}
.el-input-number__decrease:hover,
.el-input-number__increase:hover {
  color: #1d1d1f !important;
}

/* Form item spacing */
.el-form-item {
  margin-bottom: 22px !important;
}
.el-form-item:last-child {
  margin-bottom: 0 !important;
}
</style>
