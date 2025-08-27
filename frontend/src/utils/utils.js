import Vue from "vue"
import storage from "@/utils/storage"
import { STORAGE_KEY } from "@/utils/constants"
import ojAPI from "@oj/api"

export function toRoman(num) {
  num = parseInt(num)
  if (typeof num !== "number") {
    throw new TypeError("not a number")
  }
  if (num <= 0) return ""
  if (num > 10) return num
  const roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
  return roman[num - 1]
}

export function comma(value) {
  if (value === undefined || value === null) return "null"
  if (typeof value === "string") {
    return value.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
  } else {
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
  }
}

export function getTier(tier) {
  // 첫 글자 대문자로, 마지막 글자가 숫자일 경우 띄어쓰기, 숫자를 로마자로 변환, 나머지는 소문자로
  if (tier === undefined || tier === null) return "--"
  const firstUppercase = tier[0].toUpperCase() + tier.slice(1).toLowerCase()
  const lastChar = firstUppercase[tier.length - 1]
  if (isNaN(lastChar)) {
    return firstUppercase
  } else {
    const grade = firstUppercase.slice(0, -1)
    const number = parseInt(lastChar)
    return `${grade} ${toRoman(number)}`
  }
}

function submissionMemoryFormat(memory) {
  if (memory === undefined) return "--"
  // 1048576 = 1024 * 1024
  let t = parseInt(memory) / 1048576
  return String(t.toFixed(0)) + "MB"
}

function submissionTimeFormat(time) {
  if (time === undefined) return "--"
  return time + "ms"
}

function getACRate(acCount, totalCount) {
  let rate = totalCount === 0 ? 0.0 : ((acCount / totalCount) * 100).toFixed(2)
  return String(rate) + "%"
}

// 去掉值为空的项，返回object
function filterEmptyValue(object) {
  let query = {}
  Object.keys(object).forEach((key) => {
    if (object[key] || object[key] === 0 || object[key] === false) {
      query[key] = object[key]
    }
  })
  return query
}

// 按指定字符数截断添加换行，非英文字符按指定字符的半数截断
function breakLongWords(value, length = 16) {
  let re
  if (escape(value).indexOf("%u") === -1) {
    // 没有中文
    re = new RegExp("(.{" + length + "})", "g")
  } else {
    // 中文字符
    re = new RegExp("(.{" + (length / 2 + 1) + "})", "g")
  }
  return value.replace(re, "$1\n")
}

function downloadFile(url) {
  return new Promise((resolve, reject) => {
    Vue.prototype.$http
      .get(url, { responseType: "blob" })
      .then((resp) => {
        let headers = resp.headers
        if (headers["content-type"].indexOf("json") !== -1) {
          let fr = new window.FileReader()
          if (resp.data.error) {
            Vue.prototype.$error(resp.data.error)
          } else {
            Vue.prototype.$error("Invalid file format")
          }
          fr.onload = (event) => {
            let data = JSON.parse(event.target.result)
            if (data.error) {
              Vue.prototype.$error(data.data)
            } else {
              Vue.prototype.$error("Invalid file format")
            }
          }
          let b = new window.Blob([resp.data], { type: "application/json" })
          fr.readAsText(b)
          return
        }
        let link = document.createElement("a")
        link.href = window.URL.createObjectURL(
          new window.Blob([resp.data], { type: headers["content-type"] }),
        )
        link.download = (headers["content-disposition"] || "").split(
          "filename=",
        )[1]
        document.body.appendChild(link)
        link.click()
        link.remove()
        resolve()
      })
      .catch(() => {})
  })
}

function getLanguages() {
  return new Promise((resolve, reject) => {
    let languages = storage.get(STORAGE_KEY.languages)
    if (languages) {
      resolve(languages)
    }
    ojAPI.getLanguages().then(
      (res) => {
        let languages = res.data.data.languages
        storage.set(STORAGE_KEY.languages, languages)
        resolve(languages)
      },
      (err) => {
        reject(err)
      },
    )
  })
}

function xmlToJson(xml) {
  let obj = {}

  if (xml.nodeType === 1) {
    // Element node
    if (xml.attributes.length > 0) {
      obj["@attributes"] = {}
      for (let j = 0; j < xml.attributes.length; j++) {
        const attribute = xml.attributes.item(j)
        obj["@attributes"][attribute.nodeName] = attribute.nodeValue
      }
    }
  } else if (xml.nodeType === 3) {
    // Text node
    obj = xml.nodeValue
  }

  // 자식 노드를 순회
  if (xml.hasChildNodes()) {
    for (let i = 0; i < xml.childNodes.length; i++) {
      const item = xml.childNodes.item(i)
      const nodeName = item.nodeName
      if (typeof obj[nodeName] === "undefined") {
        obj[nodeName] = xmlToJson(item)
      } else {
        if (typeof obj[nodeName].push === "undefined") {
          const old = obj[nodeName]
          obj[nodeName] = []
          obj[nodeName].push(old)
        }
        obj[nodeName].push(xmlToJson(item))
      }
    }
  }
  return obj
}

export default {
  submissionMemoryFormat: submissionMemoryFormat,
  submissionTimeFormat: submissionTimeFormat,
  getACRate: getACRate,
  filterEmptyValue: filterEmptyValue,
  breakLongWords: breakLongWords,
  downloadFile: downloadFile,
  getLanguages: getLanguages,
}
