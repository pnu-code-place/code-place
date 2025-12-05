<template>
    <div class="editor-wrapper" :class="{ 'is-focused': editor && editor.focused, 'is-readonly': !editable }">
        <div class="editor-menubar" v-if="editor && editable">
            <!-- 진하게 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.bold() }"
                @click="editor.commands.bold()">
                <i class="fa fa-bold" aria-hidden="true"></i>
            </div>
            <!-- 이탤릭체 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.italic() }"
                @click="editor.commands.italic()">
                <i class="fa fa-italic" aria-hidden="true"></i>
            </div>
            <!-- 밑줄 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.underline() }"
                @click="editor.commands.underline()">
                <i class="fa fa-underline" aria-hidden="true"></i>
            </div>
            <!-- 취소선 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.strike() }"
                @click="editor.commands.strike()">
                <i class="fa fa-strikethrough" aria-hidden="true"></i>
            </div>
            <!-- 인라인 코드 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.code() }"
                @click="editor.commands.code()">
                <i class="fa fa-terminal" aria-hidden="true"></i>
            </div>

            <div class="divider"></div>
            <!-- H1 -->
            <div class="menubar__button btn-heading" :class="{ 'is-active': editor.isActive.heading({ level: 1 }) }"
                @click="editor.commands.heading({ level: 1 })">
                <span class="label-h1">H1</span>
            </div>
            <!-- H2 -->
            <div class="menubar__button btn-heading" :class="{ 'is-active': editor.isActive.heading({ level: 2 }) }"
                @click="editor.commands.heading({ level: 2 })">
                <span class="label-h2">H2</span>
            </div>
            <!-- H3 -->
            <div class="menubar__button btn-heading" :class="{ 'is-active': editor.isActive.heading({ level: 3 }) }"
                @click="editor.commands.heading({ level: 3 })">
                <span class="label-h3">H3</span>
            </div>

            <div class="divider"></div>
            <!-- 리스트 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.bullet_list() }"
                @click="editor.commands.bullet_list()">
                <i class="fa fa-list-ul list-icon" aria-hidden="true"></i>
            </div>
            <!-- 번호 리스트 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.ordered_list() }"
                @click="editor.commands.ordered_list()">
                <i class="fa fa-list-ol list-icon" aria-hidden="true"></i>
            </div>

            <div class="divider"></div>
            <!-- 코드 블럭-->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.code_block() }"
                @click="editor.commands.code_block()">
                <i class="fa fa-code" aria-hidden="true"></i>
            </div>
            <!-- 인용 -->
            <div class="menubar__button" :class="{ 'is-active': editor.isActive.blockquote() }"
                @click="editor.commands.blockquote()">
                <i class="fa fa-quote-left" aria-hidden="true"></i>
            </div>

            <div class="divider"></div>
            <!-- 되돌리기 -->
            <div class="menubar__button" @click="editor.commands.undo()">
                <Icon type="reply" size="20"></Icon>
            </div>
            <!-- 다시하기 -->
            <div class="menubar__button" @click="editor.commands.redo()">
                <Icon type="forward" size="20"></Icon>
            </div>
        </div>

        <div class="editor-content-box" :class="{ 'readonly-content': !editable }">
            <editor-content class="editor__content" :editor="editor" />
        </div>
    </div>
</template>

<script>
import { Editor, EditorContent } from 'tiptap'
import { textblockTypeInputRule } from 'tiptap-commands'
import {
    Blockquote,
    CodeBlockHighlight,
    HardBreak,
    Heading,
    OrderedList,
    BulletList,
    ListItem,
    Bold,
    Code,
    Italic,
    Strike,
    Underline,
    History,
} from 'tiptap-extensions';

// 언어별 하이라이팅 라이브러리
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';
import cpp from 'highlight.js/lib/languages/cpp';
import java from 'highlight.js/lib/languages/java';
import bash from 'highlight.js/lib/languages/bash';
import go from 'highlight.js/lib/languages/go';
import 'highlight.js/styles/atom-one-dark.css';

// 코드블럭 생성 규칙 재정의 ex) ```python 후 엔터 or space -> 코드블럭 생성
class CustomCodeBlock extends CodeBlockHighlight {
    inputRules({ type }) {
        return [
            textblockTypeInputRule(
                /^```([a-z]+)?\s$/,
                type,
                match => ({ language: match[1] || 'python' })
            ),
        ]
    }
    // 엔터로 코드블록 생성 규칙 추가
    keys({ type }) {
        return {
            'Enter': (state, dispatch) => {
                const { $from } = state.selection
                const match = $from.node().textContent.match(/^```([a-z]+)?$/)
                if (match) {
                    if (dispatch) {
                        const tr = state.tr.delete($from.start(), $from.end())
                        tr.setBlockType($from.start(), $from.start(), type, { language: match[1] || 'python' })
                        dispatch(tr)
                    }
                    return true
                }
                return false
            }
        }
    }
}

export default {
    name: 'TiptapEditor',
    components: {
        EditorContent,
    },
    props: {
        value: {
            type: String,
            default: '',
        },
        editable: {
            type: Boolean,
            default: true,
        },
    },
    data() {
        return {
            editor: null,
        }
    },
    mounted() {
        this.initEditor();
    },
    beforeDestroy() {
        if (this.editor) {
            this.editor.destroy();
        }
    },
    watch: {
        value(val) {
            if (this.editor && val !== this.editor.getHTML()) {
                this.editor.setContent(val);
            }
        },
        editable(val) {
            if (this.editor) {
                this.editor.setOptions({
                    editable: val,
                })
            }
        },
    },
    methods: {
        initEditor() {
            this.editor = new Editor({
                editable: this.editable,
                extensions: [
                    new Blockquote(),
                    new HardBreak(),
                    new Heading({ levels: [1, 2, 3] }),
                    new BulletList(),
                    new OrderedList(),
                    new ListItem(),
                    new Bold(),
                    new Code(),
                    new Italic(),
                    new Strike(),
                    new Underline(),
                    new History(),
                    // 코드 하이라이팅 설정
                    new CustomCodeBlock({
                        languages: {
                            javascript, python, cpp, java, bash, go
                        },
                    }),
                ],
                content: this.value,
                onUpdate: ({ getHTML }) => {
                    this.$emit('input', getHTML());
                },
            });
        },
    },
}
</script>

<style lang="less" scoped>
/* Editor Styles */
.editor-wrapper {
    border: 1px solid #e8ecef;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    background: #fff;

    &.is-focused {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }

    &.is-readonly {
        border: none;
        border-radius: 0;
    }
}

.editor-menubar {
    background-color: #f8f9fa;
    border-bottom: 1px solid #e8ecef;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    user-select: none;
}

.menubar__button {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    cursor: pointer;
    color: #515a6e;
    transition: all 0.2s;
    font-weight: 600;
    font-size: 14px;
    border: 1px solid transparent;

    &:hover {
        background-color: #e8ecef;
        color: #2c3e50;
    }

    &.is-active {
        background-color: #3498db;
        color: white;
        border-color: #3498db;
    }

    &.btn-heading {
        align-items: flex-end;
        padding-bottom: 5px;
    }

    .label-h1 {
        font-size: 18px;
        font-weight: 700;
        line-height: 1;
    }

    .label-h2 {
        font-size: 16px;
        font-weight: 700;
        line-height: 1;
    }

    .label-h3 {
        font-size: 14px;
        font-weight: 700;
        line-height: 1;
        padding-bottom: 1px;
    }

    .list-icon {
        font-size: 18px;
    }
}

.divider {
    width: 1px;
    height: 20px;
    background-color: #dcdee2;
    margin: 0 6px;
}

.editor-content-box {
    background: white;
    min-height: 400px;
    cursor: text;
    padding: 20px;

    &.readonly-content {
        padding: 0;
        min-height: auto;
    }
}

.editor__content {
    height: 100%;
    outline: none;
}

/* ProseMirror Content Styles */
/deep/ .ProseMirror {
    outline: none;
    min-height: 360px;
    font-size: 16px;
    line-height: 1.7;
    color: #2c3e50;

    p {
        margin-bottom: 1em;
    }

    h1,
    h2,
    h3 {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        font-weight: 700;
        line-height: 1.3;
        color: #2c3e50;
    }

    h1 {
        font-size: 1.8em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }

    h2 {
        font-size: 1.5em;
        padding-bottom: 0.3em;
    }

    h3 {
        font-size: 1.25em;
    }

    ul,
    ol {
        padding-left: 1.5em;
        margin-bottom: 1em;
    }

    li {
        margin-bottom: 0.5em;
    }

    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 16px;
        margin-left: 0;
        margin-right: 0;
        color: #7f8c8d;
        font-style: italic;
        background: #f8f9fa;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1em;
    }

    pre {
        background: #282c34;
        color: #abb2bf;
        padding: 16px;
        border-radius: 8px;
        font-family: 'Fira Code', 'Consolas', monospace;
        overflow-x: auto;
        margin-bottom: 1em;
        line-height: 1.5;

        code {
            background: none;
            padding: 0;
            color: inherit;
            font-size: 14px;
            font-family: inherit;
        }
    }

    code {
        background: #f0f3f7;
        padding: 3px 6px;
        border-radius: 4px;
        font-family: 'Fira Code', 'Consolas', monospace;
        font-size: 0.9em;
        color: #e74c3c;
    }

    a {
        color: #3498db;
        text-decoration: none;

        &:hover {
            text-decoration: underline;
        }
    }

    img {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
}

.readonly-content /deep/ .ProseMirror {
    min-height: auto;
}
</style>
