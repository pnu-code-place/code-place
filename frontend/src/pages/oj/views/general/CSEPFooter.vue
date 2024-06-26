<script>
export default {
  data() {
    return {
      version: process.env.VERSION,
      github_icon: require('@/assets/github.png'),
      github_url: "https://github.com/PNU-CSEP"
    };
  },
}

</script>

<template>
  <footer>
    <div class="footer-contents">
      <div class="row1">
        <div class="left">
          {{ $t("m.PNUCSEP") }}
        </div>
        <div class="family-site">
          <a href="https://swedu.pusan.ac.kr/swedu/index.do">소프트웨어융합교육원</a>
          <a href="https://csep.co.kr">코딩역량강화플랫폼</a>
        </div>
      </div>
      <div class="row2">
        <div class="left">
          <address>
            {{ $t("m.AddressPNUCSEP") }} <br/>
            TEL : 051-510-3737, 3738, 3624 <br/>
          </address>
          <p>
            Copyright© Pusan National Univ. All Right Reserved.
          </p>
          <p>
            Powered by
            <a href="https://github.com/QingdaoU/OnlineJudge">OnlineJudge</a>
            <span v-if="version">&nbsp; Version: {{ version }}</span>
          </p>
        </div>
        <div class="right">
          <p>
            <a :href="this.github_url">
              <img class="github-icon" :src="this.github_icon" alt="github icon">
              개발진
            </a>
          </p>
          <p>{{ $t("m.UserGuide") }}</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped lang="less">

.github-icon {
  width: 18px;
  height: 18px;
}

footer {
  position: absolute;
  bottom: 0;
  width: 100vw;
  min-width: var(--global-width);
  height: var(--footer-height);
  background-color: var(--box-background-color);
  color: var(--footer-text-color);
  font-size: 14px;
  display: flex;
  flex-direction: column;
  justify-content: end;
  align-items: center;
  padding: 20px 0;
  --footer-text-color: #ababab;

  .footer-contents {
    width: var(--global-width);
    margin: auto;
    .row1 {
      display: flex;
      justify-content: space-between;
      width: 100%;

      .left {
        font-weight: bold;
      }

      .family-site {
        display: flex;
        justify-content: end;
        gap: 10px;
        a {
          color: var(--footer-text-color);
        }
      }
    }

    .row2 {
      display: flex;
      justify-content: space-between;
      align-content: end;
      width: 100%;
      margin-top: 20px;

      .left {
        address {
          font-style: normal;
          font-weight: bold;
        }
      }
      .right {
        display: flex;
        flex-direction: column;
        justify-content: end;

        p {
          display: flex;
          justify-content: end;

          a {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: var(--footer-text-color);
            gap:5px;
          }
        }
      }
    }
  }
}

</style>
