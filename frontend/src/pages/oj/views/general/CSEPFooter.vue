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
          <p>
            <a href="https://pusanackr-my.sharepoint.com/:p:/g/personal/ehdwls1638_pusan_ac_kr/ETpnehh_9y1Hkk7LZjvp0JYBdwjSEUyNp8ARkodOpDvczA?rtime=FIVByG-q3Eg">
              {{ $t("m.UserGuide") }}
            </a>
          </p>
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
        //display: flex;
        //justify-content: end;
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
