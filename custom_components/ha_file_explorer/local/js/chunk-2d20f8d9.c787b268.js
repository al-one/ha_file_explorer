(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d20f8d9"],{b3b4:function(e,t,a){"use strict";a.r(t);var i=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("v-dialog",{attrs:{width:"500"},model:{value:e.dialog,callback:function(t){e.dialog=t},expression:"dialog"}},[a("v-card",[a("v-card-title",[e._v(" 重命名文件 ")]),a("v-card-text",[a("v-form",{on:{submit:function(t){return t.preventDefault(),e.saveClick.apply(null,arguments)}}},[a("v-text-field",{attrs:{label:"新文件名",autofocus:!0},model:{value:e.name,callback:function(t){e.name="string"===typeof t?t.trim():t},expression:"name"}})],1),a("span",{staticClass:"red--text"},[e._v(" 注意：重命名文件不能与现有文件相同 ")])],1),a("v-divider"),a("v-card-actions",[a("v-spacer"),a("v-btn",{attrs:{color:"primary",text:""},on:{click:e.saveClick}},[e._v(" 保存 ")])],1)],1)],1)},n=[],o=a("5530"),c=(a("b0c0"),a("5880")),l={data:function(){return{dialog:!1,sourceFileName:"",name:""}},computed:Object(c["mapGetters"])(["getFilePath"]),methods:Object(o["a"])(Object(o["a"])({},Object(c["mapActions"])(["operationFile"])),{},{show:function(e){this.sourceFileName=e,this.name=e,this.dialog=!0},saveClick:function(){var e=this,t=this.sourceFileName,a=this.name;if(!a)return this.$toast("请输入名称");var i=this.getFilePath(a);this.operationFile({type:"rename",name:t,rename_path:i}).then((function(t){var a=t.code;0===a&&(e.dialog=!1)}))}})},r=l,s=a("2877"),u=Object(s["a"])(r,i,n,!1,null,null,null);t["default"]=u.exports}}]);