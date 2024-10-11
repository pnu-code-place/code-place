<template>
  <div class="faq">
    <div class="section-title">{{ $t('m.Frequently_Asked_Questions') }}</div>

    <nav class="faq-nav">
      <div class="nav-item">채점 프로그램</div>
      <div class="nav-item">문제</div>
      <div class="nav-item">대회</div>
      <div class="nav-item">계정</div>
    </nav>

    <ul class="content markdown-body">
      <FAQItem :question="this.$t('m.Where_is_the_input_and_the_output')">
        <div class="markdown-body">
          <p>{{ $t('m.Where_is_the_input_and_the_output_answer_part_1') }} <code>stdin</code>
            ('{{ $t('m.Standard_Input') }}') {{ $t('m.Where_is_the_input_and_the_output_answer_part_3') }}
            <code>stdout</code>
            ('{{ $t('m.Standard_Output') }}') {{ $t('m.Where_is_the_input_and_the_output_answer_part_5') }}
            <code>scanf</code>
            {{ $t('m.Where_is_the_input_and_the_output_answer_part_6') }} <code>cin</code>
            {{ $t('m.Where_is_the_input_and_the_output_answer_part_7') }} <code>printf</code>
            {{ $t('m.Where_is_the_input_and_the_output_answer_part_8') }} <code>cout</code>
            {{ $t('m.Where_is_the_input_and_the_output_answer_part_9') }} <code>{{ $t('m.Runtime_Error') }}</code>.
          </p>
        </div>
      </FAQItem>
      <FAQItem :question="$t('m.What_is_the_meaning_of_submission_execution_time')">
        <p>{{ $t('m.What_is_the_meaning_of_submission_execution_time_answer') }}
        </p>
      </FAQItem>
      <FAQItem :question="$t('m.How_Can_I_use_CPP_Int64')">
        <p>{{ $t('m.How_Can_I_use_CPP_Int64_answer_part_1') }}<code>long long</code>
          {{ $t('m.How_Can_I_use_CPP_Int64_answer_part_2') }} <code>cin/cout</code> {{ $t('m.or') }} <code>%lld</code>,
          {{ $t('m.using') }}<code> __int64</code> {{ $t('m.How_Can_I_use_CPP_Int64_answer_part_3') }}
          <code>{{ $t('m.Compile_Error') }}</code>.</p>
      </FAQItem>
      <FAQItem :question=" $t('m.Java_specifications')">
        <p>{{ $t('m.Java_specifications_answer_part_1') }} <code>Main</code>
          {{ $t('m.Java_specifications_answer_part_2') }} <code>Main</code>
          {{ $t('m.Java_specifications_answer_part_3') }}</p>
      </FAQItem>
      <FAQItem :question="$t('m.About_presentation_error')">
        <p>{{ $t('m.About_presentation_error_answer_part_1') }} <b>{{ $t('m.last') }}</b>
          {{ $t('m.About_presentation_error_answer_part_2') }} <code> {{ $t('m.Wrong_Answer') }}</code>.</p>
      </FAQItem>
      <FAQItem :question="$t('m.How_to_report_bugs')">
        <p>{{ $t('m.How_to_report_bugs_answer_part_1') }} <a
          href="https://evening-mirror-c09.notion.site/a7568fd7e0334a509c081567223cd454?pvs=4" target="_blank">Notion Link</a>
          {{ $t('m.How_to_report_bugs_answer_part_2') }}
        </p>
      </FAQItem>
    </ul>
  </div>
</template>

<script>
import {defineComponent} from "vue";
import FAQItem from "./FAQItem.vue";

export default defineComponent({
  components: {FAQItem}
})
</script>

<style lang="less" scoped>
.faq {
  width: var(--global-width);

  .faq-nav {
    width: 100%;
    border: 1px solid #dedede;
    border-radius: 7px;
    display: flex;
    background-color: var(--box-background-color);
    margin-bottom: 20px;

    .nav-item {
      font-size: 16px;
      padding: 10px;
      width: 100%;
      text-align: center;
      border-right: 1px solid #dedede;

      &:last-child {
        border-right: none
      }
    }
  }
}

.content {
  font-size: 16px;
  display: flex;
  flex-direction: column;
  border-radius: 7px;
  overflow: hidden;
  border: 1px solid #dedede;

  > ul {
    list-style: disc;
  }
}
</style>
