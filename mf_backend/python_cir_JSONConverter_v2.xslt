<?xml version="1.0"?>
<!-- ********************************* @author CIBILMaheshwari.Wagish ************************************************** -->
<xsl:stylesheet
version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt"
xmlns:usr="urn:the-xml-files:xslt" extension-element-prefixes="msxsl">
    <xsl:output method="html"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <META http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <title>CIBIL: CONSUMER INFORMATION REPORT</title>
                <!-- <link href="/CIBIL/cibilstyle/css/style.css" rel="stylesheet" type="text/css" /> -->
                <style type="text/css">
					/* CSS Document */
					body.MainBody {margin:0px; padding:0px; text-align:center;}
					.maincontainer {margin:0px auto;width:827px; border:0px solid #c9c9c9; color:#000000; font-family:Arial, Helvetica, sans-serif; font-size: 11px;}

					/* Headaer */


					.headerlogo1{
					width:300px;
					height:65px;
					background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABBCAYAAABrYJlFAAAAAXNSR0IB2cksfwAAG3hJREFUeJztXQmcHUWZL45FQEVRFg9QV0QxLG6QG1ZYLlFB5HBZTpFTATkUUI6wZIHl2EWQcCUhM5nX3TM5hvsKp4wIhiMz87r7zUwOjpCQgBIkEA2QQBi//1ev+1VV97tm5r3Jm6n/71e/SV53V1VXd/37q6++QwgLi5GGlmA34YVXCNefIxz/XeEG/Vpx/LeFFzwknPA8MW3uF4e7uxYWFqMNM2dvRER0OBHSI/T3LSKr94QTfED//iiFsPDbaiYzJwB5TWWSs7CwsKg5pr/wJeGG04iA3iAiei+VpEoVJ/g7/V1If68Szd3/PNy3Y2FhMVKRye1DBDWXyCZl6QcJK3iZ/v0ElYn07yaSpp6l8xenSl2Ov4Iks1miLfzmcN+WhYXFSMKsBR8j8jmFSGYelQ8NAgpEJrhYuD37Mvm4/leF1/cF0dT1ReF2bS2c3BiSyA4VXthEJPYX49qVVF8X1b3NcN+ihYXFSEBH//qitedUIqIXiWDWKFLSPCKaM0QLkdSt4aZifMf6ReuYAMKb8wXR1rMLXXclEddKRTL7UBJh+B91vCsLC4sRh/Hj1yVS2o+IpTuWrPhv+CRJTAeRRLUpnbVOxfW196/HO4VucAKVrLFMfFxMDb5Vu5uxsLAY2chktyAJ6CEik1UKucwgotpRtHRsOOB63dc/ThLVgSS1zWYJi+vFTqN/s2h/6VNDeAcWFhajBk5uHBHJigJZ+U9S2Y4lpcFi8tKNqf4fEmEtUOpfTBLdf4rx/esOQe8tLCxGDUBM2g6f3yXc3B5D2gbbcwXH5E0dsCxcQ+VR0RxuNaTtWFhYjHC4gafol/5M5SRNsprcuTFJQ3sKN3so/f3RgPVP3oJNqI3LFCX8O1R+Ko5oH7wUZ2FhMQrQ0rM9EdTf8mQFC/bJoq1zM+0cL9iBiOUuVp47/nP070MG3t5zn8/bb0V6sieYEC0sLCzKwvUvUpaCi0Qme5jo79d3AzP+8Xlr934mNxDYoNoMTyyQJC0RYaRqYWFhURZu8HBMWHBc9oItteMtCzdk1xr4CMrz+gYtEUFvpUpZTtA6qPosLCxGCRw/spFaTcRxU2JXcHruS/T73YoUdsug27xu9kZU1wXU9vux3sx7dpNB12thYTHCoRNWk5hgEIcT7k7nvKBIYfsNTbvh/uwYHUtZ1vrdwsKiHNzgKUUB3peXfI4kSerHXBz/Ci32FfwMo2OtXV9hC3go4eVvB4sm+i1G/zrC7dk6Pt/1940POf43hBs+ptR78TDcvYWFRUPB8a9JDwlDUpUsrxluNS/kJa45wu3+LhHS94l4wvzvHcLL7R3X3dGxPv3/HOWa5vgY9GAc6cHP+yz69w7D3VtYWDQUpFlDb1VxriRxZUUmuwv9+7exO4+DEDNdY+K6pa7qLuW6q7W23eCSQvgav6/et25hYdGIyARHE2ncT+RBUpD/15SwMmnB+e4QLdl/oXPhwrMmH4lhpraDiNAzUKhH/oNu+F2tXZg3uEFkLrGY6vt0vW/dwsKiEcG6pvBsIpbfEfnMJALBzuBchaBeo/IA/46SCX8uvLnb0LH5+eMIi/w/ep1EUIXrXxBTu7+uH88dTMcW5QnrdXYRsrCwsBgQXH+KIlU1J0wPXP+oOFCfQ5IZCEiFF96sLCGnJcIku/73451CS1gWFhYDBgLxFcjkA9EanKoF7mtvX094wbWxLRWC/rX0fL5w/ayP0bGXRBxS2T9PtPdsoLVhCcvCwmJI0Bp8S5GOlibspFx/cyKi+xSD0ntLXA+H6h8m2sBvcAeKl5y5MYlzLCwsLGIgHtXNHZ/g8MgqEEWhoH/q4PDI2vFwJyKbTsXw86xCnePXFW72AoWwnhEt2e0TbXvhcbFS3vGX2FyGFhYW6cDyrLX3K2zJ7uZOZkNOFY5/oaK/ckXzgqT+KVryScNPmVwCoWLaer+uB+sLZiSul22cKzPq8Dnza3ezFhYWjQ1kvHH99kJI5PBE7bhHZFIgnIeJ1May2QEs25vmfpKz47jBkgJh9e3Ax3jn0G/TQi07wXQxLfycUGPCg9jc4EblnN/XeQQsLCwaBlN6PkNEcWecHNULbmVXmgjwGYys0KFY53jvwQSSyJpExj+fI5K6fqAs++bR30lFjFDfpN8vZSkMUh2ID1Eh3PAeRQd2wzCOhoWFxVoPN3sj7wBKCSfHEUEj4N/J3IL5dPT+g2IqR3GA0n1NCkFFCVQ/KGJ4eonIBHtRPaqd18CDAlpYWIwCeKxYXxbv5CEphArHP0sahCop6iUREdH4u9Lfn8hlob9GJzSOnbWE42u5kM6061cLL7czSWqnFUwi6Px7aJlpYWFhURTY+YtCx7A7jj+F7a8iSAflS6gs1wmLpDEo3QHHP63gfhO54AQPixnzx3J6MNSpR3u4m8Mke2qMreCB4RoCCwuLRoJuzZ4VLZ27Jc6BzgmOzojE0FokAQWOocC/0AQs3KHzwvG7F35atPUhxlYhIzQStVpYWFiUBdtTqfol///FzT2fqGmbehKKLLX58Zq2Z2FhMULQzuYFhSB+TvCyaOv5Ts3ac/3TRSE+PJaIv9ZcfgYKLGUd/ztxUZe2FhXA8ZcPSXH9DLtBWOhwOr+cT62ujFdwVcXXZ7IXGGP9R7ZNqhXuW7qxaM39hF1YnGAch15ZWzB9/hgijxV5HdUaNleohdV5JviBps9yw6cSFvTVANl7PHrmDhK/Bss5E09U5P+7aLl5adnn6vivVD4fg/sL13HblV73HF/r4dnnjWzT+3JadRwRHsjXQUrFO6wfv7DywSwXT6ji4t/OSkoLHdCV6OF9+zk0SqVw/fH6NjyWJl1b16y/XvjfAtE7OWCd/yaVK9eafHyQcBCIrzAeJAH5j4n2IVwayqVnt9LGcpq454hZA5CEps9FHC5EgkBk1Hc0iU0vq+n423JXM3e+aHo6fSdSEkqlc7Ijvg7vW6XXYXdUbkgsZw8BhOIxo1cAGRqTavghMgcBYfHyWjnmGeF+SsISVm3RSIR1G4wk/cfj7X1pGvAkSXn/WpP2BgI4HrvB88oEW0USUJvwFmxZ/uJydfvfzt9/3uYLO5JhOxFi9e91S7AbS04I5ayaS5QmizVC7nTO0GzNCv2rPWHp/fmIiRZJP5q6dEnWEtYIRSMRVnpf0x2ChwuTO/9JuNkjqG8vKmPyNkcWdbp2GlCdcKx2/O/xvWtLwaBHtPXswserASJGcHz4ohJVubKC55Mp2dSbsArEhfE9Qwu7M3yE5c9JL5zu+y2j4UVFz/fCa4Tz3GererCjAY1EWFhaIdW7oxhYwi3FTFo63MBL7wW/pL5GxqSQYGB+QEs5/2wxM2UJUwxt4VasX5LLNsWv0F/KkUhBkNWAY88HfyoxcXP0dya1OZH/yv+nkcS7ojX8HSeIjeBAt5g7WZagWUT6PFnvMklM+eNteZ2RHC+TsHBdkDqPZX/eS+lTjyaQQOqO+8L96TBI6EHteJSlaPCElRubWlqC/YS+rdvPW8lFz6eJORS7KCMNjURYCLfCz93vyy8HICUcI8a3b1D+4joDGzzQLUl9SzTJP5Bxq/zHqJzPu3BNKZbpkzs/xQal/JH1/6QblAbS39Dr3U/MXLxRVX1iO65gktYnWR8s5R/gMDVQwCMEM94L/GWFPP/+UAq5vaxZ9aPfsDVD4V1M6Bjjd2oRpyiLjqsmH0nC6hatwQ9S5zH6k8kexhmG9HtYxW5KERD4MGqLfS79qYl3XD0eEf+gCasYkla+1OnsLwdf8ShDIxEW97djQ35psaxpC3cU7TRJ1lZMmf0ZjodlOjLLyKGv5aUFGnsfUuJNMg6830HlaangDt403HVW5d109q3648uRTcP/EmpkCNmXd+j364Xbt52YOTudAPF7K0lmnE4seEcjYCdoTVV6e3zfy5S2FsZW/SaShPVUquFsfC+09IPJiEylppLWpUWvkRJj4dxWI/NQoS+WsNZqNBphNRoQvz2TPUDqsIwJVhjv94WMxLAs/ThPxrdkbPfuPRIhkivBlPBzVEeL0BypOXrEdDG97xtl9WDt/evxhoLjI93YaqVf87TErvF915CwAARKdAypzwvcoudbwhohsIRVe2CyN3dvK9zszwSnAYudlcsXqQfzaDl0FD8r1DUQZLp2pGe12Kh/Du88YqldCTgCKhK+qlIaLS8RZ97UpdWasGQbNxnXPVHi3AYhLESAlF8WlMm09j0zttuBFS/8stzgMjo2VZ4T3MpGZ4g3pMY1AvBlk/GLzs+f11Io9H/YqOBrahqo4mFil0e9xvVPFm3zNpP19m9AA7gX9e0irU43ezXnuqskzxy2dd3w2Lzeo0WvJ/gVL6FUBWk8jjUkLGmN3RyPj0f3Mjm/hMPE42ib4aV0fErcVy+8QiBVO4LYpcEL9qRrzhNIBY8CnVYpZMJ/E17256zf1MaFDSEPLmpM7PYiisIN+b430fnnspFthKndO1Nfz2I7psIzvYX6dILw5qQbs+LeOWkqPacM9K3hLDYudfxX85LPSg4VwwacCApIEwXp7uF3eF2R5Vol4LEOfsFLUX0i/rpqAsQ9QJLRiaJZtHVupp1XD8KC0l+/nweLntswhOXlDlDEVzywVwQy52LgEVrW9WcLh5NeRrY9q1iZiG3baPcJ4jLW+JIM/sg7NOqOTXSdGywV0hJ3BpXfiLb5W/H1k5duzBNb3+UhUTp7Jk8CGEPKLWtDuYrtcL+XJsv1iVx0EUCGXvCjfJt9mo6h0Nar+Z2hy9lYUBvHmhLWH0QU54nHFboc+kJjXHFPTvA8SxBIHqoufaTF9eWpZIJxlS//67LQxya9X5tLkvEfZQND119h9HOZtEPyW5m4TBcULziloDRmPRLCvFzM9YKIoWuCIlmVluTznc/k1RbuXnKZxclRw52o7C+c7kMEQsw43cdI8wVaYiHzjdP32cRHcyCQ0R7ajHdiGcfiGghas9tL3Vy+ZLL7JIx360FY5nvrBROKnts4hBUelDKB3+CvC1IqFRXFQRQ9Xxb99MJw3KGAXuzgzaLn6wVK1cX8BQaQnAAkqdePSfAEfWX/lydDSeM9H/qNa/LhcQtgIqWX2wt+L4pbKav1vE73MkGT2GpJWEjDbvbBC29lXUwasZokC3IylxqOf4W+y5XSV4wTXDekKUA5o8j3JZkboY0hkajhYGSZzQSJXcqSfWdd1QyOyb42ADtyjm/sqgX31bTNWhIWrPqxO6maTUgSOqZEfxqEsGSAtK6ERJRcz5sT61r2W8vkviZD0Pppth+lCwYJ4HhIvIx8Q5Mm2L0geK3C+pbwUkLdHYK0xLYy6lceqc7RDrb8ufzVqGc5SwjxONZSwgrvFVFguwIRLRbSR62Se16YSItVjrCkDdQ5ecKr/FlhVw5L1giZ7HF0Lz2azZd0X3ldVJSCnu/xkqrtpGoBXk2YO2rhSTVtczCE5fg99NvxfL5ZWnOHs9rACXzjne3iuVq8Pw1CWBCrYdDm8FIt7cVCJEjE1O6gzj7JqcDxskMyg5LRy12VJDuI/dixwWTlpd6VghWj+XTjJmGBZORWPA00L2PMPqzipSlLYVRfJrhOIKVTkmTbYimL+0ZLQf2lWM27PohwiRdGFpq8AdKiqzs7YWEca7okRAr13xQZdyJW2BjRMlvW8dvEixLds/Y8yxCWjDJg2uiAYBbIcQhbhMup4v+c0q9s/GXnoHy85En/oMiAfRPz7wBJyf6DKef0irv6ht9YGXpcs29tg3CWrgSDI6y3BTwYpLGnWTCPlws9+uqrbOmOpW/x/jQIYQEQidmoNPHiLeHByoSHCS+7N7H3PszsrbQcyGS34CBsSb3SE6xvUG1P2B2DJqkbjjdudKLeZ3pJ1IQDcrA/4IkEQ7nIgXXCs5sQyX6P9S96f7HE+basix6Ow8setW8PCa972+RD6N01QUq35fVztd4lnMWZj1OkEP9ettSOlMlwqG0NDuHxNV9edazLSljGiyl3saYJN3ssu/Dgfr3unQUv+WDAaSylMaYqOPpEChFB2o0sq1mPyHVOTJ4b7l/xWNYK6IPZr7QNmKHE4JaElRfpDH17WZ1XQxEWb8ciQ4n2Yv6dd3hATNq5/euyoZzUD91mvPwvspUtjPDSYOrLTMLCRHaMwYCCP0OSUlqdUoIylLoktUARCwtpR4ty2c+K4jTAIhq7V3iwUYn0K/Uwa0i8ZCS1tGT/PbW+DIwbzWWsYudTirCkJfcio70Zwu0em2iH/fPCA4XqqCzH+Bkt9x/MEPS+r6TnfG563+ldcpSEEPxMSKoebqTpcWveZt0IaxVv7mA3vVTsroYiLMB0hsSLNbUzPUxtVD+Wh4VrQBxXp7pSRBgYYU0XLUW87SGdJHy5/NOZ3CCRsJmGeowkvLRQK9g4wNKYpcB8iaS54SGspqL1YecKS3P9WZ0WHy9FWHD90NtamEpWESDdweRDV64vYem20Pf7jbF5RkwvsbuW2FypsXK7EqQRVq0D8w1uSfg+f9SkuYdesHGUlkWIsxXRB754fxqcsNQAYmmQ+eSWKYP4atEBj6+pkrCkCcW4ohIbX8NOpEqduXNYJwZfKemPppgEsJ7mDLZNgv0RvvjlwvQOB2EheWgxwP7KlGxhThChFGGZLyWIsdzE5B1gNqOIrkN8qTOUvpuEdYMoFYrYDY8w7vepku3XA7hH8xnAqbqmbQ6GsOhcmBBFtnZq4XhoweT8ct7YxQ2fpKVuus1i4xMWLadKQUYsVLzN6avv9ST1QyqqJ6y3ii7j4jppsNIIS7C5xd5Uh2GawZM5S9fdQX+vYyPLluyx8tyeL3OmYG0ch4GwSil800xA3PCW+HhJCcvwyMdmSzmXExAkIkAUngnCt1yu1GkuCceVVO5KfeHaRVjsTG3q6mhsaola22Hhg4z3wrwvM8VaoT8jnrD0iYGlm2nNa6J6wlrGD7ZkncUIi4D+YHI5MFj10xNxyr5jEuZ3IXN7aJN4OAiLvQiKINVmjcY+QlWEZZhEFIP0BojaglnIJKXOKgkLUQXWMsKCGsN0es4EMwZcH6T2ls5vxqWZpLWk4W3tDUchJcpM2eq1Xuq5o4+w6PxyoXjrTVhcp785x1V3g0fkw2OrfdMMQ51wMCXYPb4+TWc0mglLPpcWpc7GJyxsImnp7Pk+/lJUd1oOeM89eiZRgfGzGfGzHoQl35UbjWfnp/d5tBGWWwFhwdK23oQVt00k4IUnCfZng8kAS1R5P7VgpX7v4WPxvUzpQQiUR42HPqkipSx78LMNmnptZ8LlY7gIq5zOEWCTFLahi/r/IY9hoc7GJ6wOjjV/gWG0jPKLqqOVSiPo240xuSOx214Pwko17fGXp5478gmLB0KZ6BVEtkwqi+tHWMm+wOdtVyHtjaYJxF/SHliuYFbgsLW84sLiP1bUd1EFjFhVHzUZVK8jEf6kfoR1vzH+5VNfoS+qvZuMD1UwWxgJhAW09u6VNJaF43VuDO8iVwKcJ/0cFyvP/EN20jads+tBWHKX9zKDsJalnjviCSsTHif0XYjnYqPNNMh05AvqR1j08mByq6VoHQs2obau13cUlbFyggnGMvJFtvcqtXspxDoycoKiQ4AbSyab1I3Ui7DgSaC39TBLkMXA3gK0vNHNV95go9BC30cGYcEUw2HJW9V10jiGt8nlXBnSwljNnL8FXeMKR4uHBTewIxPn10eHtSn3R5/Xc1PPHfGEBT0P1vmFB/M33jlM8w3Dw3RyhycmZi0JC36OmFhqXOpS4j2221UfPp2wfsqRIfQv1V0lc93hJXf8/zPumSZA7vTEufUiLEQN0CYTh2s5qqg/H0uI4S3GBHyB454X+j70hIXnhGikmHClPwpDBxlx9KSEUa5MkHEV++EVk0bxu9MH957rtPcEHyh4VzSnmEjUmrDwTFt7kZ/RNDJuSz1/5BMWDC0N30BYRWfCHVmaisRo2ENJJ+Q5iYkJw04VQ0lYHEHScABtn/fVVPEeuqZM9kzj/s8utLFgS0PKyLdF/WcXJY55vTGL4DKC5hbSL9LQjeF+mtNcg+pEWNxWIpLCXA7jggQWkUkHJi8kL2n9b/p26vZ5gyesp7XjICt4Gci2jy9JFEMNmLVIv1JDl4XxJMmYcx76m8dxzkGo/J7hdzqeiAUPsgvP47oxttB7YmxkGOtThBOodoyvsNQeHUeJ3tWk4egzHANMjbkelVvZTm9zDt9jrmhAoK15cw3o7dS2vNBU11yrHY/igqUT1rX8caukFEWtCQvwQlOCQIEvIPRC2+X9Bw9l1wAZp/sjw7zgTn7oUbKAISUsnnAPGPd0D4n+X+PJGT8oIpip7Of2vPEQjtbaAUmk7S5CaZ9hRf7p3FckLnURXypx3ho6PjX1HupKWOHPEhMrimWFicebE8FurFhPxgRfmfD9GzxhzWWil1E91+GPG+KyZzi44QX8HjpdY4rWN9TgcM2G+5D+Dv2BA+PJ4HiT2Bgz7TyWrvwH4kCLyAoNKb41dyQXDlapxX9HSKer4uMobYuia00JCyYYzXE/1AKTEyfoEGYwQtn3ReKeuZ+Uvp19O2htecbGEnTS2vGebfPueEnCkkbjz1RUiqIehIU04665w1aywBFTjZm1Qj44Wi7ygxlCwsLXTKaJV4PfrWFiQhwu3nrmcqFIfImCdxMp1O9hW53ZKTtJ5QvbLvmvpSbX5PuuI2Fl5m/BL2e198ETIGU5UTVhdY9N2sT5P2b9D/t0hmfngxji3b2Tl2PsH1pHuNkTRTUJVNOfN03inq2VOk9I+VCUqSeUeRoHm5cwmntOPv4cJDEnET653D2Nywc6TBJWNaUo6kFYcjBPruhByO3wx/MhZD5KbWuodwlh7SvD0BQ3Gk32cxWJ279KbQskhmVmmq9Wqfv2glxJmyfzmloSlhyzPen3sOJxkaF3OkT7S8kMPNUSlozIkQwhFOllWoPLOFIGpFFEyHT9i0RLBeYXQ42W7EFscOxwGvpKMz9/JN3J/E5esqkYLsKSfXqfxvK+eINlVBMWct4lXEVSB65X3L2Q1v0cFubd1LZqYdaAkCyc863CAfXClhITbh0xY/5YIUMbV/qQspxyqVQig3oTFreJgG9Q9FYyJvQeFcsKXjVhpbyXKmGx9NtzND9Xxyfpl30T6ythRWifuw3Ni8qTYsjzZqaO1fARFlZAE8UkJY7+qCYsbotuBOtcmTDAXGos5wkWmRVw7K3gEm1HrpaExfUi/nfqJIna+ZD7jnsoNdniNhGPKziVrYaL19nLCT0qSZAxHIQFwJLb4Tj8yeijLH0hm3Du+JIO4tUSFgBn4wyyPKcQFtvHBY/kAyuO48mmJreoN2Az52UP4A+ZGuRRH6tl/A4jgUYx1JuwZJDGiWJqSoqxYSSsfwADdipr2SGE9wAAAABJRU5ErkJggg==);
					background-repeat:no-repeat;
					margin-bottom: 30px;
					margin-left: 17px;
					}
					}

					#ccir{
					margin-top:10px;
					}

					.details{
					width:256px;
					height:103px;
					background:url(../images/Details.jpg);
					}

					.headerlogo2{
					background:url(../images/logo2.jpg);
					width:435px;
					height:80px;
					position:absolute;
					float:left;

					}

					.summary{
					color:#ffffff;
					font-family:font-family:Arial, Helvetica;
					font-size:10px;
					padding-left:54px;
					}

					.constitle5{
					background-color:#CEE0E8;
					font-family:Arial, Helvetica, sans-serif;
					font-size:12px;
					font-weight:bold;
					color:#305665;
					padding-left: 300px;
					}


					.addressinfo{   font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9; font-weight:bold; padding-left:20px;padding-bottom:2px;
					}
					.timezone{
					width:150px;
					height:20px;
					margin-top:14px;
					margin-left:18px;
					}


					.head1 { font-family:"Times New Roman", Times, serif; font-size:16px; color:#34748e; text-transform:uppercase;font-weight:bold; padding-left: 7px; width:610px;}
					.headtitle1 { font-family:"Times New Roman", Times, serif; font-size:17px; color:#34748e; text-transform:uppercase;font-weight:bold; padding-left: 7px; width:610px;}
					.headtitle2 { font-family:Arial, Helvetica, sans-serif;font-size:13px; color:#656565;text-transform:uppercase;}
					.headtitle3 { font-family:Arial, Helvetica, sans-serif;font-size:15px; color:#34748e;text-transform:uppercase; padding-top: 15px; font-weight:normal;}
					.headtitle4 { font-family:Arial, Helvetica, sans-serif;font-size:16px; color:#34748e;text-transform:uppercase; padding-top: 7px; font-weight:Bold;}

					.headlabel {font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9; font-weight:normal; padding-left:10px;padding-bottom:2px;}
					.headlabe2 {font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9; font-weight:normal; padding-left:30px;padding-bottom:2px;}
					.headvalue {font-family:Arial, Helvetica, sans-serif;text-transform:uppercase;color:#000000;padding-bottom:2px;font-size:12px;}

					.headborder { border-bottom:3px solid #34748e; padding-top:10px;}
					.headborder2 { border-bottom:1px solid #818284; padding-top:5px;}

					/* Consumer Details */
					.constitle { background-color:#00a6ca;font-family:Arial, Helvetica, sans-serif;font-size:14px; font-weight:bold; color:#ffffff;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle1 { background-color:#CEE0E8;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle1_shay{ background-color:#6fa7bc;font-family:Arial, Helvetica, sans-serif;font-size:13px;  color:#ffffff;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle1_cen { background-color:#CEE0E8;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; text-align:center;color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle4_cen { background-color:#CEE0E8;font-family:Arial, Helvetica, sans-serif;font-size:12px; text-align:center;color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle1_cen_shay_o{ background-color:#DDD;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; text-align:center;color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle1_cen_shay_yi{ background-color:#FFF;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; text-align:center;color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}

					.constitle1_gry { background-color:#F0F0F0;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; color:#305665;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.consubtitle { font-family:Arial, Helvetica, sans-serif;font-size:10px; color:#005586;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.constitle2 { background-color:#FFF;font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#4f90a9;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle3 { background-color:#FFF;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; color:#346070; padding-left: 3px; padding-top: 5px;padding-bottom: 5px; padding-left:10px; text-transform:uppercase}
					.constitle3_Cen { background-color:#FFF;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; text-align:center; color:#4f90a9;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle3_Left { background-color:#FFF; border:0px solid #4f90a9; font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; text-align:left; color:#4f90a9;padding-left: 3px; padding-top: 5px;padding-bottom: 0px;}
					.constitle1_gry { background-color:#E0E0E0;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; color:#000000;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}
					.constitle4 { background-color:#4f90a9;font-family:Arial, Helvetica, sans-serif;font-size:14px; color:#ffffff;padding-left: 3px; padding-top: 5px;padding-bottom: 5px;}


					/*.padWhole {padding:5px 15px 10px 20px;}
					.padWhole2 {padding:15px 15px 0px 20px;}
					.padWhole3{padding:0px 15px 0px 20px;}
					.padWhole4 {padding:0px 15px 0px 20px;}
					.padWhole5{padding:1px 15px 0px 20px;}*/
					.conLabel{font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:normal;padding-bottom:5px;padding-top:5px;}
					.conValue{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal;padding-bottom:5px;padding-top:5px;}
					.conValueAddPad{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal;padding:3px;}
					.conValueAddPad_Cen{background-color:#FFF;font-size:11px;font-family:Arial, Helvetica, sans-serif;color:#000000; text-align:center;font-weight:normal;padding:5px;}
					.conValueAddPad_left_shay{background-color:#FFF;font-size:11px;font-family:Arial, Helvetica, sans-serif;color:#000000; text-align:left;font-weight:normal;padding:5px;}
					.conValueAddPad_AlignC{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal; text-align:center; padding:5px;}
					.conValueAddPad_AlignC_bld{background-color:#FFF;font-size:14px;font-family:Arial, Helvetica, sans-serif;color:#000000; font-weight:bold; text-align:center; padding:5px;}

					.conValueAddPad_Cen_shay_yi{background-color:#FFF;font-size:11px;font-family:Arial, Helvetica, sans-serif;color:#000000; text-align:left;font-weight:normal;padding:5px;}
					.conValueAddPad_Cen_shay_o{background-color:#DDD;font-size:11px;font-family:Arial, Helvetica, sans-serif;color:#000000; text-align:left;font-weight:normal;padding:5px;}

					.padLeft {padding-left:5px;}
					.conValuepadLeft{padding-left:5px;background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal;padding-bottom:5px;padding-top:5px;}

					.conValueBoldAddPad {background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:bold;padding:5px;}
					.conValueSpec{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:normal;padding-bottom:5px;padding-top:5px;}
					.conValueSpecAddPad{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:normal;padding:5px;}
					.conValueSpecAddPad_1{background-color:#CCC;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#305665;font-weight:bold; text-align:center;padding:5px;}
					.conValueSpecAddPad_cen{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;text-align:center;color:#6D7B8D;font-weight:normal;padding:5px;}
					.conValueSpecAddPad_shay{background-color:#FFF;font-size:11px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:normal;padding:2px;}
					.conValueSpecAddPad_shay_2{background-color:#4f90a9;font-size:10px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:normal;padding:2px;}
					.conValueSpecAddPad_shay1{background-color:#DDD;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#305665;font-weight:bold; text-align:center;padding:5px;}
					.conValueSpecAddPad_shay3{background-color:#FFF;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#4f90a9;font-weight:bold;padding:2px;}


					.constitleblue { background-color:#4f90a9;font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#FFF; padding-bottom:3px;}
					.constitleblueAddPad { background-color:#4f90a9;font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#FFF; padding:5px;}
					.constitleblueAddPad_Cen { background-color:#4f90a9;font-family:Arial, Helvetica, sans-serif;font-size:12px; text-align:center; color:#FFF; padding:5px;}
					.constitleblueAddPad2 { background-color:#ffffff;font-family:Arial, Helvetica, sans-serif;font-size:12px; font-weight:bold; color:#457E94; padding:5px; padding-left:10px}
					.Scorevalue {font-family:Arial, Helvetica, sans-serif;font-size:9px; color:#1a1a1a;text-transform:uppercase;padding-left:5px;border-bottom:1px solid #85afd9;}
					.Score {font-family:Arial, Helvetica, sans-serif;color:#003365; font-size:32px;border-bottom:1px solid #85afd9;}
					ol{ padding-left:15px}
					.AddPad { padding:5px;}
					.ThreeColtable { background-color:#fff;font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#FFF; padding:1px;}
					.ThreeColtable_left { background-color:#ffffff;font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#FFF; border-right:1px solid #4f90a9;}

					.Matrixtable_Subtitle {background-color:#E0E0E0;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:bold;padding:3px;}
					.Matrixtable_text {background-color:#E0E0E0;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal;padding:3px;}
					.Matrixtable_text_bld {background-color:#F0F0F0;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#000000; font-weight:bold; padding:3px;}
					.Matrixtable_text_Blu_bld {background-color:#fff;font-size:12px;font-family:Arial, Helvetica, sans-serif;color:#305867; text-align:center; font-weight:bold; padding:3px;}
					.Matrixtable_text_Cen { background-color:#fff;font-family:Arial, Helvetica, sans-serif;font-size:12px; text-align:center; color:#000000; padding:5px;}
					.specBorder{border:1px solid #aaaaaa; padding:5px;}
					.specconstitle{font-family:Arial, Helvetica, sans-serif;color:#656565;text-transform:uppercase; font-weight:bold; font-size:9px; padding-bottom:3px;}
					.specconValue{font-family:Arial, Helvetica, sans-serif;color:#1c1c1c;text-transform:uppercase; font-weight:bold;font-size:9px;padding-bottom:3px;}

					.borderBot{border-bottom:1px solid #CCCCCC;}
					.daysTitle{font-family:Arial, Helvetica, sans-serif;color:#000;text-transform:uppercase; font-weight:normal;font-size:9px;padding-bottom:3px;}
					.daysValue{font-family:Arial, Helvetica, sans-serif;color:#000;text-transform:uppercase; font-weight:normal;font-size:9px;padding-bottom:3px;}

					.endStatement{font-family:Arial, Helvetica, sans-serif;color:#000000;font-weight:normal;font-size:9px;padding-bottom:5px; text-align:justify;}

					.specBg{background-color:#f3f3f3;}

					.BGcolor0{ background-color:#4f90A9;}
					/*.BGcolor0{ background-color:#0070b0;}*/

					.BGcolor1{ background-color:#A0C5D3;}
					.BGcolor2{ background-color:#F7F7F7;}
					.BGcolor3{ background-color:#FFFFFF;}
					.BGcolor4{ background-color:#DFDFDF;}

					/*.BGcolor1{ background-color:#31697e;}*/

					/* By Nataraj */


					.TUCibilheaderlogo1{
					width:300px;
					height:65px;
					background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABBCAYAAABrYJlFAAAAAXNSR0IB2cksfwAAG3hJREFUeJztXQmcHUWZL45FQEVRFg9QV0QxLG6QG1ZYLlFB5HBZTpFTATkUUI6wZIHl2EWQcCUhM5nX3TM5hvsKp4wIhiMz87r7zUwOjpCQgBIkEA2QQBi//1ev+1VV97tm5r3Jm6n/71e/SV53V1VXd/37q6++QwgLi5GGlmA34YVXCNefIxz/XeEG/Vpx/LeFFzwknPA8MW3uF4e7uxYWFqMNM2dvRER0OBHSI/T3LSKr94QTfED//iiFsPDbaiYzJwB5TWWSs7CwsKg5pr/wJeGG04iA3iAiei+VpEoVJ/g7/V1If68Szd3/PNy3Y2FhMVKRye1DBDWXyCZl6QcJK3iZ/v0ElYn07yaSpp6l8xenSl2Ov4Iks1miLfzmcN+WhYXFSMKsBR8j8jmFSGYelQ8NAgpEJrhYuD37Mvm4/leF1/cF0dT1ReF2bS2c3BiSyA4VXthEJPYX49qVVF8X1b3NcN+ihYXFSEBH//qitedUIqIXiWDWKFLSPCKaM0QLkdSt4aZifMf6ReuYAMKb8wXR1rMLXXclEddKRTL7UBJh+B91vCsLC4sRh/Hj1yVS2o+IpTuWrPhv+CRJTAeRRLUpnbVOxfW196/HO4VucAKVrLFMfFxMDb5Vu5uxsLAY2chktyAJ6CEik1UKucwgotpRtHRsOOB63dc/ThLVgSS1zWYJi+vFTqN/s2h/6VNDeAcWFhajBk5uHBHJigJZ+U9S2Y4lpcFi8tKNqf4fEmEtUOpfTBLdf4rx/esOQe8tLCxGDUBM2g6f3yXc3B5D2gbbcwXH5E0dsCxcQ+VR0RxuNaTtWFhYjHC4gafol/5M5SRNsprcuTFJQ3sKN3so/f3RgPVP3oJNqI3LFCX8O1R+Ko5oH7wUZ2FhMQrQ0rM9EdTf8mQFC/bJoq1zM+0cL9iBiOUuVp47/nP070MG3t5zn8/bb0V6sieYEC0sLCzKwvUvUpaCi0Qme5jo79d3AzP+8Xlr934mNxDYoNoMTyyQJC0RYaRqYWFhURZu8HBMWHBc9oItteMtCzdk1xr4CMrz+gYtEUFvpUpZTtA6qPosLCxGCRw/spFaTcRxU2JXcHruS/T73YoUdsug27xu9kZU1wXU9vux3sx7dpNB12thYTHCoRNWk5hgEIcT7k7nvKBIYfsNTbvh/uwYHUtZ1vrdwsKiHNzgKUUB3peXfI4kSerHXBz/Ci32FfwMo2OtXV9hC3go4eVvB4sm+i1G/zrC7dk6Pt/1940POf43hBs+ptR78TDcvYWFRUPB8a9JDwlDUpUsrxluNS/kJa45wu3+LhHS94l4wvzvHcLL7R3X3dGxPv3/HOWa5vgY9GAc6cHP+yz69w7D3VtYWDQUpFlDb1VxriRxZUUmuwv9+7exO4+DEDNdY+K6pa7qLuW6q7W23eCSQvgav6/et25hYdGIyARHE2ncT+RBUpD/15SwMmnB+e4QLdl/oXPhwrMmH4lhpraDiNAzUKhH/oNu+F2tXZg3uEFkLrGY6vt0vW/dwsKiEcG6pvBsIpbfEfnMJALBzuBchaBeo/IA/46SCX8uvLnb0LH5+eMIi/w/ep1EUIXrXxBTu7+uH88dTMcW5QnrdXYRsrCwsBgQXH+KIlU1J0wPXP+oOFCfQ5IZCEiFF96sLCGnJcIku/73451CS1gWFhYDBgLxFcjkA9EanKoF7mtvX094wbWxLRWC/rX0fL5w/ayP0bGXRBxS2T9PtPdsoLVhCcvCwmJI0Bp8S5GOlibspFx/cyKi+xSD0ntLXA+H6h8m2sBvcAeKl5y5MYlzLCwsLGIgHtXNHZ/g8MgqEEWhoH/q4PDI2vFwJyKbTsXw86xCnePXFW72AoWwnhEt2e0TbXvhcbFS3vGX2FyGFhYW6cDyrLX3K2zJ7uZOZkNOFY5/oaK/ckXzgqT+KVryScNPmVwCoWLaer+uB+sLZiSul22cKzPq8Dnza3ezFhYWjQ1kvHH99kJI5PBE7bhHZFIgnIeJ1May2QEs25vmfpKz47jBkgJh9e3Ax3jn0G/TQi07wXQxLfycUGPCg9jc4EblnN/XeQQsLCwaBlN6PkNEcWecHNULbmVXmgjwGYys0KFY53jvwQSSyJpExj+fI5K6fqAs++bR30lFjFDfpN8vZSkMUh2ID1Eh3PAeRQd2wzCOhoWFxVoPN3sj7wBKCSfHEUEj4N/J3IL5dPT+g2IqR3GA0n1NCkFFCVQ/KGJ4eonIBHtRPaqd18CDAlpYWIwCeKxYXxbv5CEphArHP0sahCop6iUREdH4u9Lfn8hlob9GJzSOnbWE42u5kM6061cLL7czSWqnFUwi6Px7aJlpYWFhURTY+YtCx7A7jj+F7a8iSAflS6gs1wmLpDEo3QHHP63gfhO54AQPixnzx3J6MNSpR3u4m8Mke2qMreCB4RoCCwuLRoJuzZ4VLZ27Jc6BzgmOzojE0FokAQWOocC/0AQs3KHzwvG7F35atPUhxlYhIzQStVpYWFiUBdtTqfol///FzT2fqGmbehKKLLX58Zq2Z2FhMULQzuYFhSB+TvCyaOv5Ts3ac/3TRSE+PJaIv9ZcfgYKLGUd/ztxUZe2FhXA8ZcPSXH9DLtBWOhwOr+cT62ujFdwVcXXZ7IXGGP9R7ZNqhXuW7qxaM39hF1YnGAch15ZWzB9/hgijxV5HdUaNleohdV5JviBps9yw6cSFvTVANl7PHrmDhK/Bss5E09U5P+7aLl5adnn6vivVD4fg/sL13HblV73HF/r4dnnjWzT+3JadRwRHsjXQUrFO6wfv7DywSwXT6ji4t/OSkoLHdCV6OF9+zk0SqVw/fH6NjyWJl1b16y/XvjfAtE7OWCd/yaVK9eafHyQcBCIrzAeJAH5j4n2IVwayqVnt9LGcpq454hZA5CEps9FHC5EgkBk1Hc0iU0vq+n423JXM3e+aHo6fSdSEkqlc7Ijvg7vW6XXYXdUbkgsZw8BhOIxo1cAGRqTavghMgcBYfHyWjnmGeF+SsISVm3RSIR1G4wk/cfj7X1pGvAkSXn/WpP2BgI4HrvB88oEW0USUJvwFmxZ/uJydfvfzt9/3uYLO5JhOxFi9e91S7AbS04I5ayaS5QmizVC7nTO0GzNCv2rPWHp/fmIiRZJP5q6dEnWEtYIRSMRVnpf0x2ChwuTO/9JuNkjqG8vKmPyNkcWdbp2GlCdcKx2/O/xvWtLwaBHtPXswserASJGcHz4ohJVubKC55Mp2dSbsArEhfE9Qwu7M3yE5c9JL5zu+y2j4UVFz/fCa4Tz3GererCjAY1EWFhaIdW7oxhYwi3FTFo63MBL7wW/pL5GxqSQYGB+QEs5/2wxM2UJUwxt4VasX5LLNsWv0F/KkUhBkNWAY88HfyoxcXP0dya1OZH/yv+nkcS7ojX8HSeIjeBAt5g7WZagWUT6PFnvMklM+eNteZ2RHC+TsHBdkDqPZX/eS+lTjyaQQOqO+8L96TBI6EHteJSlaPCElRubWlqC/YS+rdvPW8lFz6eJORS7KCMNjURYCLfCz93vyy8HICUcI8a3b1D+4joDGzzQLUl9SzTJP5Bxq/zHqJzPu3BNKZbpkzs/xQal/JH1/6QblAbS39Dr3U/MXLxRVX1iO65gktYnWR8s5R/gMDVQwCMEM94L/GWFPP/+UAq5vaxZ9aPfsDVD4V1M6Bjjd2oRpyiLjqsmH0nC6hatwQ9S5zH6k8kexhmG9HtYxW5KERD4MGqLfS79qYl3XD0eEf+gCasYkla+1OnsLwdf8ShDIxEW97djQ35psaxpC3cU7TRJ1lZMmf0ZjodlOjLLyKGv5aUFGnsfUuJNMg6830HlaangDt403HVW5d109q3648uRTcP/EmpkCNmXd+j364Xbt52YOTudAPF7K0lmnE4seEcjYCdoTVV6e3zfy5S2FsZW/SaShPVUquFsfC+09IPJiEylppLWpUWvkRJj4dxWI/NQoS+WsNZqNBphNRoQvz2TPUDqsIwJVhjv94WMxLAs/ThPxrdkbPfuPRIhkivBlPBzVEeL0BypOXrEdDG97xtl9WDt/evxhoLjI93YaqVf87TErvF915CwAARKdAypzwvcoudbwhohsIRVe2CyN3dvK9zszwSnAYudlcsXqQfzaDl0FD8r1DUQZLp2pGe12Kh/Du88YqldCTgCKhK+qlIaLS8RZ97UpdWasGQbNxnXPVHi3AYhLESAlF8WlMm09j0zttuBFS/8stzgMjo2VZ4T3MpGZ4g3pMY1AvBlk/GLzs+f11Io9H/YqOBrahqo4mFil0e9xvVPFm3zNpP19m9AA7gX9e0irU43ezXnuqskzxy2dd3w2Lzeo0WvJ/gVL6FUBWk8jjUkLGmN3RyPj0f3Mjm/hMPE42ib4aV0fErcVy+8QiBVO4LYpcEL9qRrzhNIBY8CnVYpZMJ/E17256zf1MaFDSEPLmpM7PYiisIN+b430fnnspFthKndO1Nfz2I7psIzvYX6dILw5qQbs+LeOWkqPacM9K3hLDYudfxX85LPSg4VwwacCApIEwXp7uF3eF2R5Vol4LEOfsFLUX0i/rpqAsQ9QJLRiaJZtHVupp1XD8KC0l+/nweLntswhOXlDlDEVzywVwQy52LgEVrW9WcLh5NeRrY9q1iZiG3baPcJ4jLW+JIM/sg7NOqOTXSdGywV0hJ3BpXfiLb5W/H1k5duzBNb3+UhUTp7Jk8CGEPKLWtDuYrtcL+XJsv1iVx0EUCGXvCjfJt9mo6h0Nar+Z2hy9lYUBvHmhLWH0QU54nHFboc+kJjXHFPTvA8SxBIHqoufaTF9eWpZIJxlS//67LQxya9X5tLkvEfZQND119h9HOZtEPyW5m4TBcULziloDRmPRLCvFzM9YKIoWuCIlmVluTznc/k1RbuXnKZxclRw52o7C+c7kMEQsw43cdI8wVaYiHzjdP32cRHcyCQ0R7ajHdiGcfiGghas9tL3Vy+ZLL7JIx360FY5nvrBROKnts4hBUelDKB3+CvC1IqFRXFQRQ9Xxb99MJw3KGAXuzgzaLn6wVK1cX8BQaQnAAkqdePSfAEfWX/lydDSeM9H/qNa/LhcQtgIqWX2wt+L4pbKav1vE73MkGT2GpJWEjDbvbBC29lXUwasZokC3IylxqOf4W+y5XSV4wTXDekKUA5o8j3JZkboY0hkajhYGSZzQSJXcqSfWdd1QyOyb42ADtyjm/sqgX31bTNWhIWrPqxO6maTUgSOqZEfxqEsGSAtK6ERJRcz5sT61r2W8vkviZD0Pppth+lCwYJ4HhIvIx8Q5Mm2L0geK3C+pbwUkLdHYK0xLYy6lceqc7RDrb8ufzVqGc5SwjxONZSwgrvFVFguwIRLRbSR62Se16YSItVjrCkDdQ5ecKr/FlhVw5L1giZ7HF0Lz2azZd0X3ldVJSCnu/xkqrtpGoBXk2YO2rhSTVtczCE5fg99NvxfL5ZWnOHs9rACXzjne3iuVq8Pw1CWBCrYdDm8FIt7cVCJEjE1O6gzj7JqcDxskMyg5LRy12VJDuI/dixwWTlpd6VghWj+XTjJmGBZORWPA00L2PMPqzipSlLYVRfJrhOIKVTkmTbYimL+0ZLQf2lWM27PohwiRdGFpq8AdKiqzs7YWEca7okRAr13xQZdyJW2BjRMlvW8dvEixLds/Y8yxCWjDJg2uiAYBbIcQhbhMup4v+c0q9s/GXnoHy85En/oMiAfRPz7wBJyf6DKef0irv6ht9YGXpcs29tg3CWrgSDI6y3BTwYpLGnWTCPlws9+uqrbOmOpW/x/jQIYQEQidmoNPHiLeHByoSHCS+7N7H3PszsrbQcyGS34CBsSb3SE6xvUG1P2B2DJqkbjjdudKLeZ3pJ1IQDcrA/4IkEQ7nIgXXCs5sQyX6P9S96f7HE+basix6Ow8setW8PCa972+RD6N01QUq35fVztd4lnMWZj1OkEP9ettSOlMlwqG0NDuHxNV9edazLSljGiyl3saYJN3ssu/Dgfr3unQUv+WDAaSylMaYqOPpEChFB2o0sq1mPyHVOTJ4b7l/xWNYK6IPZr7QNmKHE4JaElRfpDH17WZ1XQxEWb8ciQ4n2Yv6dd3hATNq5/euyoZzUD91mvPwvspUtjPDSYOrLTMLCRHaMwYCCP0OSUlqdUoIylLoktUARCwtpR4ty2c+K4jTAIhq7V3iwUYn0K/Uwa0i8ZCS1tGT/PbW+DIwbzWWsYudTirCkJfcio70Zwu0em2iH/fPCA4XqqCzH+Bkt9x/MEPS+r6TnfG563+ldcpSEEPxMSKoebqTpcWveZt0IaxVv7mA3vVTsroYiLMB0hsSLNbUzPUxtVD+Wh4VrQBxXp7pSRBgYYU0XLUW87SGdJHy5/NOZ3CCRsJmGeowkvLRQK9g4wNKYpcB8iaS54SGspqL1YecKS3P9WZ0WHy9FWHD90NtamEpWESDdweRDV64vYem20Pf7jbF5RkwvsbuW2FypsXK7EqQRVq0D8w1uSfg+f9SkuYdesHGUlkWIsxXRB754fxqcsNQAYmmQ+eSWKYP4atEBj6+pkrCkCcW4ohIbX8NOpEqduXNYJwZfKemPppgEsJ7mDLZNgv0RvvjlwvQOB2EheWgxwP7KlGxhThChFGGZLyWIsdzE5B1gNqOIrkN8qTOUvpuEdYMoFYrYDY8w7vepku3XA7hH8xnAqbqmbQ6GsOhcmBBFtnZq4XhoweT8ct7YxQ2fpKVuus1i4xMWLadKQUYsVLzN6avv9ST1QyqqJ6y3ii7j4jppsNIIS7C5xd5Uh2GawZM5S9fdQX+vYyPLluyx8tyeL3OmYG0ch4GwSil800xA3PCW+HhJCcvwyMdmSzmXExAkIkAUngnCt1yu1GkuCceVVO5KfeHaRVjsTG3q6mhsaola22Hhg4z3wrwvM8VaoT8jnrD0iYGlm2nNa6J6wlrGD7ZkncUIi4D+YHI5MFj10xNxyr5jEuZ3IXN7aJN4OAiLvQiKINVmjcY+QlWEZZhEFIP0BojaglnIJKXOKgkLUQXWMsKCGsN0es4EMwZcH6T2ls5vxqWZpLWk4W3tDUchJcpM2eq1Xuq5o4+w6PxyoXjrTVhcp785x1V3g0fkw2OrfdMMQ51wMCXYPb4+TWc0mglLPpcWpc7GJyxsImnp7Pk+/lJUd1oOeM89eiZRgfGzGfGzHoQl35UbjWfnp/d5tBGWWwFhwdK23oQVt00k4IUnCfZng8kAS1R5P7VgpX7v4WPxvUzpQQiUR42HPqkipSx78LMNmnptZ8LlY7gIq5zOEWCTFLahi/r/IY9hoc7GJ6wOjjV/gWG0jPKLqqOVSiPo240xuSOx214Pwko17fGXp5478gmLB0KZ6BVEtkwqi+tHWMm+wOdtVyHtjaYJxF/SHliuYFbgsLW84sLiP1bUd1EFjFhVHzUZVK8jEf6kfoR1vzH+5VNfoS+qvZuMD1UwWxgJhAW09u6VNJaF43VuDO8iVwKcJ/0cFyvP/EN20jads+tBWHKX9zKDsJalnjviCSsTHif0XYjnYqPNNMh05AvqR1j08mByq6VoHQs2obau13cUlbFyggnGMvJFtvcqtXspxDoycoKiQ4AbSyab1I3Ui7DgSaC39TBLkMXA3gK0vNHNV95go9BC30cGYcEUw2HJW9V10jiGt8nlXBnSwljNnL8FXeMKR4uHBTewIxPn10eHtSn3R5/Xc1PPHfGEBT0P1vmFB/M33jlM8w3Dw3RyhycmZi0JC36OmFhqXOpS4j2221UfPp2wfsqRIfQv1V0lc93hJXf8/zPumSZA7vTEufUiLEQN0CYTh2s5qqg/H0uI4S3GBHyB454X+j70hIXnhGikmHClPwpDBxlx9KSEUa5MkHEV++EVk0bxu9MH957rtPcEHyh4VzSnmEjUmrDwTFt7kZ/RNDJuSz1/5BMWDC0N30BYRWfCHVmaisRo2ENJJ+Q5iYkJw04VQ0lYHEHScABtn/fVVPEeuqZM9kzj/s8utLFgS0PKyLdF/WcXJY55vTGL4DKC5hbSL9LQjeF+mtNcg+pEWNxWIpLCXA7jggQWkUkHJi8kL2n9b/p26vZ5gyesp7XjICt4Gci2jy9JFEMNmLVIv1JDl4XxJMmYcx76m8dxzkGo/J7hdzqeiAUPsgvP47oxttB7YmxkGOtThBOodoyvsNQeHUeJ3tWk4egzHANMjbkelVvZTm9zDt9jrmhAoK15cw3o7dS2vNBU11yrHY/igqUT1rX8caukFEWtCQvwQlOCQIEvIPRC2+X9Bw9l1wAZp/sjw7zgTn7oUbKAISUsnnAPGPd0D4n+X+PJGT8oIpip7Of2vPEQjtbaAUmk7S5CaZ9hRf7p3FckLnURXypx3ho6PjX1HupKWOHPEhMrimWFicebE8FurFhPxgRfmfD9GzxhzWWil1E91+GPG+KyZzi44QX8HjpdY4rWN9TgcM2G+5D+Dv2BA+PJ4HiT2Bgz7TyWrvwH4kCLyAoNKb41dyQXDlapxX9HSKer4uMobYuia00JCyYYzXE/1AKTEyfoEGYwQtn3ReKeuZ+Uvp19O2htecbGEnTS2vGebfPueEnCkkbjz1RUiqIehIU04665w1aywBFTjZm1Qj44Wi7ygxlCwsLXTKaJV4PfrWFiQhwu3nrmcqFIfImCdxMp1O9hW53ZKTtJ5QvbLvmvpSbX5PuuI2Fl5m/BL2e198ETIGU5UTVhdY9N2sT5P2b9D/t0hmfngxji3b2Tl2PsH1pHuNkTRTUJVNOfN03inq2VOk9I+VCUqSeUeRoHm5cwmntOPv4cJDEnET653D2Nywc6TBJWNaUo6kFYcjBPruhByO3wx/MhZD5KbWuodwlh7SvD0BQ3Gk32cxWJ279KbQskhmVmmq9Wqfv2glxJmyfzmloSlhyzPen3sOJxkaF3OkT7S8kMPNUSlozIkQwhFOllWoPLOFIGpFFEyHT9i0RLBeYXQ42W7EFscOxwGvpKMz9/JN3J/E5esqkYLsKSfXqfxvK+eINlVBMWct4lXEVSB65X3L2Q1v0cFubd1LZqYdaAkCyc863CAfXClhITbh0xY/5YIUMbV/qQspxyqVQig3oTFreJgG9Q9FYyJvQeFcsKXjVhpbyXKmGx9NtzND9Xxyfpl30T6ythRWifuw3Ni8qTYsjzZqaO1fARFlZAE8UkJY7+qCYsbotuBOtcmTDAXGos5wkWmRVw7K3gEm1HrpaExfUi/nfqJIna+ZD7jnsoNdniNhGPKziVrYaL19nLCT0qSZAxHIQFwJLb4Tj8yeijLH0hm3Du+JIO4tUSFgBn4wyyPKcQFtvHBY/kAyuO48mmJreoN2Az52UP4A+ZGuRRH6tl/A4jgUYx1JuwZJDGiWJqSoqxYSSsfwADdipr2SGE9wAAAABJRU5ErkJggg==);
					background-repeat:no-repeat;
					margin-bottom: 10px;
					margin-top: 20px;
					}

					.constitleGreyBig { font-family:Arial, Helvetica, sans-serif;font-size:14px; color:#656565;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.constitleRedBig { font-family:Arial, Helvetica, sans-serif;font-size:14px; color:Red;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.conslabelBlueBig { font-family:Arial, Helvetica, sans-serif;font-size:11px; color:#00678e;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;padding-left:5px}
					.conslabelBlackBig { font-family:Arial, Helvetica, sans-serif;font-size:11px; color:Black;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.conslabelScoreBig { font-family:Arial, Helvetica, sans-serif;font-size:28px; color:#00678e;text-transform:uppercase; padding-bottom: 10px;}

					.yellowheader {background-color:#fad700;font-weight: 500;font-size: large;}
					.blueborder { border-bottom:2.5px solid #00a7d4; padding-bottom:5px;}
					.greyborder25 { border-bottom:2.5px solid #878787; padding-bottom:5px;}
					.greyborder { border-bottom:0.5px solid #878787; padding-bottom:5px;}
					.greybordernopadding { border-bottom:1.5px solid #878787;}
					.greyallborder15 { border:1.5px solid #878787; padding-bottom:5px;}
					.padAll5 {padding:5px;}
					.padAll2 {padding:2px;}
					.BlueLabel{ color:#00a7d4;font-size: 10px; font-weight: bold; font-family: Arial, Helvetica, sans-serif; font-stretch: ultra-expanded;}
					.BlueLabelBigger1{ color:#00a7d4;font-size: 11.5px; font-weight: 700; font-family: Arial, Helvetica, sans-serif; font-stretch: ultra-expanded;}
					.BlueLabelBigger2{ font-family:Arial, Helvetica, sans-serif;font-size:11px; color:00a7d4;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.BlueLabelBigger3 { font-family:Arial, Helvetica, sans-serif;font-size:12px; color:#00a7d4;text-transform:uppercase; font-weight:bold; padding-bottom: 10px;}
					.RedLabel{ color:#d84042;font-size: 10px; font-weight: bold; font-family: Arial, Helvetica, sans-serif; font-stretch: ultra-expanded;}
					.BlackLabel{ color:Black;font-size: 11px; font-weight: bold; font-family: Arial, Helvetica, sans-serif; font-stretch: ultra-expanded;}
					.GreyItalicLabel{ color:Grey;font-size: 11px;font-style: italic; font-family: Arial, Helvetica, sans-serif; font-stretch: ultra-expanded;}
					.alternatetdbggrey {background-color:#f0f0f0;}
					.alternatetdbgwhite {background-color:#ffffff;}
					.PhDiv50Width{padding:10px;display: inline-block!important;width:35px}
					.textalignend {text-align:end}

					.backclr:nth-of-type(2n) { background-color: #f0f0f0;}
				</style>
            </head>
			
            <body class="MainBody">
			
                <xsl:variable name="ConsumerName" select="Root/root/consumerCreditData/names"/>
                <xsl:choose>
                    <xsl:when test="Root/root/controlData/errorResponseArray/item/errorMessage != ''">
                        <table cellpadding="0" cellspacing="0" border="0" class="maincontainer">
                            <tr>
                                <td width="300px">
                                    <div class="TUCibilheaderlogo1"></div>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <table width="100%" border="0" align="right" class="blueborder" cellpadding="0" cellspacing="0">
                                        <tr class="yellowheader">
                                            <td width="300px" class="padAll5">CONSUMER CIR</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <tr>
                                            <td style="color:red" colspan="4" class="constitleblueAddPad2" align="left">
                                                <xsl:for-each select="Root/root/controlData/errorResponseArray/item">
                                                    <xsl:if test="errorMessage != ''">
                                                        <xsl:call-template name="ErrorMessage">
                                                            <xsl:with-param name="ErrMsg" select="string(errorMessage)"/>
                                                        </xsl:call-template>
													</xsl:if>
                                                </xsl:for-each>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td align="left" colspan="2" class="padWhole">
                                    <table  cellpadding="0" cellspacing="0"  width="100%">
                                        <tr>
                                            <td class="endStatement AddPad " style="font-size:11px;">
                                                <p>
                                                    <strong>
														All information contained in this credit report has been collated by TransUnion CIBIL Limited (TU CIBIL) based on information provided / submitted by 
														its various members ("Members"), as part of periodic data submission and Members are required to ensure accuracy, completeness and veracity of the 
														information submitted. The credit report is generated using the proprietary search and match logic of TU CIBIL. TU CIBIL uses its best efforts to 
														ensure accuracy, completeness and veracity of the information contained in the Report, and shall only be liable and / or responsible if any 
														discrepancies are directly attributable to TU CIBIL. The use of this report is governed by the terms and conditions of the Operating Rules for TU CIBIL 
														and its Members.
													</strong>
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr style="margin-top:4px;">
                                <td align="left" colspan="2" class="padWhole" style="padding-top:11px; padding-bottom:7px;" valign="top">
                                    <table cellpadding="0" cellspacing="0" width="100%" style="border-top: 1.5px solid #00a6c9;">
                                        <tr>
                                            <td width="100%" align="center"  style="font-size:11px;font-weight: bolder">© 2023 TransUnion CIBIL Limited. (Formerly: Credit Information Bureau (India) Limited). All rights reserved</td>
                                        </tr>
                                        <tr>
                                            <td></td>
                                        </tr>
                                        <tr>
                                            <td width="100%" align="center"  style="font-size:11px;font-weight: bolder">TransUnion CIBIL CIN : U72300MH2000PLC128359</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </xsl:when>
                    <xsl:otherwise>
                        <table cellpadding="0" cellspacing="0" border="0" class="maincontainer">
                            <tr>
                                <td width="300px">
                                    <div class="TUCibilheaderlogo1"></div>
                                </td>
                            </tr>
                            <!-- Report Header Start -->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="blueborder" cellpadding="0" cellspacing="0">
                                        <tr class="yellowheader">
                                            <td width="300px" class="padAll5">CONSUMER CIR</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <tr>
                                            <td width="300px">
                                                <table>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">CONSUMER:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:value-of select="Root/root/consumerCreditData/item/names/item/name"/>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">MEMBER ID:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:value-of select="Root/root/consumerCreditData/item/tuefHeader/enquiryMemberUserId"/>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">MEMBER REFERENCE NUMBER:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:value-of select="Root/root/consumerCreditData/item/tuefHeader/memberRefNo"/>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td width="330px"></td>
                                            <td width="370px">
                                                <table>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">DATE:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(Root/root/consumerCreditData/item/tuefHeader/dateProcessed)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">TIME:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:call-template name="formatTime">
                                                                <xsl:with-param name="inpTime" select="string(Root/root/consumerCreditData/item/tuefHeader/timeProcessed)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="BlueLabel"  align="left" colspan="2">CONTROL NUMBER:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:choose>
                                                                <xsl:when test="Root/root/consumerCreditData/item/tuefHeader/enquiryControlNumber != ''">
                                                                    <xsl:value-of select="Root/root/consumerCreditData/item/tuefHeader/enquiryControlNumber"/>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Report Header End -->
							
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- Consumer Information Start -->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greyborder" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">CONSUMER INFORMATION:</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <tr>
                                            <td width="600px">
                                                <table>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">NAME:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <!-- in CIR MR is there. check Mr. Ms to add -->
                                                            <xsl:value-of select="Root/root/consumerCreditData/item/names/item/name"/>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">DATE OF BIRTH:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">                                                            
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(Root/root/consumerCreditData/item/names/item/birthDate)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td width="300px">
                                                <table>
                                                    <tr>
                                                        <td height="14px"  bgcolor="#FFFFFF"></td>
                                                    </tr>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">GENDER:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <xsl:call-template name="Getgender">
                                                                <xsl:with-param name="gender" select="string(Root/root/consumerCreditData/item/names/item/gender)"/>
                                                            </xsl:call-template>                                                            
														</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Consumer Information End -->
							
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- Consumer Score Segement Start -->
                            <xsl:if test="Root/root/consumerCreditData/item/scores/item">
                                <tr>
                                    <td>
                                        <table width="1000" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="300px" class="constitleGreyBig">CIBIL TRANSUNION SCORE(S):</td>
                                                <td width="330px"></td>
                                                <td width="370px"></td>
                                            </tr>
                                            <tr>
                                                <td width="150px" class="BlueLabel">SCORE NAME</td>
                                                <td width="150px" class="BlueLabel">SCORE</td>
                                                <td width="700px" class="BlueLabel">SCORING FACTORS</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <xsl:for-each select="Root/root/consumerCreditData/item/scores/item">
                                    <xsl:variable name="scoreV">
                                        <xsl:call-template name="getScore">
                                            <xsl:with-param name="score" select="string(score)"/>
                                        </xsl:call-template>
                                    </xsl:variable>
                                    <xsl:if test="scoreCardName != '02'">
                                        <tr>
                                            <td>
                                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                                    <tr style="height: 50px;background-color: #ededed!important;">
                                                        <td width="250px" class="conslabelBlueBig">
                                                            <xsl:choose>
                                                                <xsl:when test="scoreName = 'CIBILTUSC2'">
																	CIBIL TRANSUNION SCORE 
                                                                    <br> VERSION 2.0</br>
                                                                </xsl:when>
                                                                <xsl:when test="scoreName = 'CIBILTUSCR'">
																	CIBIL TRANSUNION SCORE 
                                                                    <br> VERSION 1.0</br>
                                                                </xsl:when>
                                                                <xsl:when test="scoreName = 'CIBILTUSC3'">
																	CREDITVISION® SCORE
																</xsl:when>
                                                                <xsl:when test="scoreName = 'CIBILTUIE1'">
																	ESTIMATED INCOME BAND
																</xsl:when>
                                                                <xsl:when test="scoreName= 'CIBILTUIE2'">
																	ESTIMATED INCOME BAND
																</xsl:when>
                                                                <xsl:otherwise>
																</xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                        <td width="250px" class="conslabelScoreBig">
                                                            <xsl:value-of select="$scoreV"/>
                                                        </td>
                                                        <td width="500px" class="conslabelBlackBig padAll5">
                                                            <ol class="padAll2">
                                                                <xsl:choose>
                                                                    <xsl:when test="$scoreV = '-1'">
                                                                        <li class="padAll2">INSUFFICIENT HISTORY TO SCORE.</li>
                                                                        <xsl:call-template name="generateScoringFactors">
                                                                            <xsl:with-param name="counter">1</xsl:with-param>
                                                                            <xsl:with-param name="ForScore">
                                                                                <xsl:value-of select="scoreCardName"/>
                                                                            </xsl:with-param>
                                                                        </xsl:call-template>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>														
                                                                        <xsl:call-template name="generateScoringFactors">
                                                                            <xsl:with-param name="counter">1</xsl:with-param>
                                                                            <xsl:with-param name="ForScore">
                                                                                <xsl:value-of select="scoreCardName"/>
                                                                            </xsl:with-param>
                                                                        </xsl:call-template>
                                                                    </xsl:otherwise>
                                                                </xsl:choose>
                                                            </ol>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </xsl:if>
                                    <xsl:if test="scoreCardName = '02'">
                                        <tr>
                                            <td colspan="4" height="3px" bgcolor="#FFFFFF"></td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                                    <tr style="height: 50px;background-color: #ededed!important;">
                                                        <td width="250px" class="conslabelBlueBig">
                                                            <xsl:choose>
                                                                <xsl:when test="scoreName = 'PLSCORE'">
																	PERSONAL LOAN SCORE
																</xsl:when>
                                                                <xsl:otherwise>

																</xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                        <td width="250px" class="conslabelScoreBig">
                                                            <xsl:value-of select="$scoreV"/>
                                                        </td>
                                                        <td width="500px" class="conslabelBlackBig padAll5">
                                                            <ol class="padAll2">
                                                                <xsl:choose>
                                                                    <xsl:when test="$scoreV = '-1'">
                                                                        <li class="padAll2">INSUFFICIENT HISTORY TO SCORE.</li>
                                                                        <xsl:call-template name="generateScoringFactors">
                                                                            <xsl:with-param name="counter">1</xsl:with-param>
                                                                            <xsl:with-param name="ForScore">
                                                                                <xsl:value-of select="scoreCardName"/>
                                                                            </xsl:with-param>
                                                                        </xsl:call-template>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>
                                                                        <xsl:call-template name="generateScoringFactors">
                                                                            <xsl:with-param name="counter">1</xsl:with-param>
                                                                            <xsl:with-param name="ForScore">
                                                                                <xsl:value-of select="scoreCardName"/>
                                                                            </xsl:with-param>
                                                                        </xsl:call-template>
                                                                    </xsl:otherwise>
                                                                </xsl:choose>
                                                            </ol>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </xsl:if>
                                </xsl:for-each>
                            </xsl:if>
							
                            <!-- TRL Score. Commented for the release -->
                            <xsl:if test="Root/root/CreditReport/ScoreSegment/TRLScore != ''">
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr style="height: 50px;background-color: #ededed!important;">
                                            <td width="250px" class="conslabelBlueBig">
													TRL SCORE
												</td>
                                            <td width="250px" class="conslabelScoreBig">
                                                <xsl:value-of select="Root/root/CreditReport/ScoreSegment/TRLScore"/>
                                            </td>
                                            <td width="500px" class="conslabelBlackBig padAll5">
												</td>
                                        </tr>
                                    </table>
                                </td>
                            </xsl:if>
                            <!-- Consumer Score Segement End -->
							
                            <!-- Credit Vsion Segement Start. Commented for the release -->
                            <xsl:if test="Root/root/consumerCreditData/item/bureauCharacteristics != ''">
                                <xsl:variable name="NoNTCVarCount" select="count(Root/root/consumerCreditData/item/bureauCharacteristics/item[featureName!='N_DM001S' and featureName!='N_DM201S' and featureName !='N_DM202S' and featureName !='N_DM212S' and featureName !='N_DM216S' and featureName !='N_G106S' and featureName !='N_G232S' and featureName !='N_G242F' and featureName !='N_G406S' and featureName !='N_G412S' and featureName !='N_G503S' and featureName !='N_G518S' and featureName !='N_DM203S' and featureName !='N_G507S' and featureName !='N_G409S' and featureName !='N_G960S' and featureName !='N_G500S' and featureName !='N_DM206S' and featureName !='N_DM211S' and featureName !='N_DM004S'])" />
                                <xsl:if test="$NoNTCVarCount > 0">
                                    <tr>
                                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                    </tr>
                                    <tr>
                                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td colspan="4" width="600px" class="constitleGreyBig">CREDIT VISION VARIABLE(S):</td>
                                                    <td width="200px"></td>
                                                </tr>
                                                <tr>
                                                    <td class="BlueLabel" style="width=20%;">CREDIT SEGMENT</td>
                                                    <td style="width=80%;">
                                                        <table style="width:100%;">
                                                            <tr>
                                                                <td style="width:10%;" class="BlueLabel">ALGORITHM</td>
                                                                <td style="width:60%;" class="BlueLabel">ALGORITHM DESCRIPTION</td>
                                                                <td style="width:10%;" class="BlueLabel">ACTUAL VALUE</td>
                                                                <td style="width:20%;" class="BlueLabel">LOW RISK TO HIGH RISK</td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <!--<xsl:variable name="show_paybe"><xsl:for-each select="Root/root/consumerCreditData/item/item/bureauCharacteristics/item"><xsl:if test="usr:get_paybe(string(featureName))">
																1	
															</xsl:if></xsl:for-each>
													</xsl:variable>-->
													
                                            <xsl:variable name="show_paybe">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">							
                                                    <xsl:variable name="payBeVal">
                                                        <xsl:call-template name="get_paybe">
                                                            <xsl:with-param name="data" select="featureName"/>	
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:if test="$payBeVal='true'">
																1
													</xsl:if>
                                                    <!-- <xsl:if test="usr:get_paybe(local-name())">
																1
													</xsl:if> -->
                                                </xsl:for-each>
                                            </xsl:variable>
											
                                            <xsl:if test="contains($show_paybe,'1')">
                                                <!--<tr style="background-color: #f0f0f0!important;">-->
                                                <tr class="backclr">
                                                    <td style="width=20%;" class="BlackLabel padAll5">
																Payment Behaviour
															</td>
                                                    <td style="width=80%;">
                                                        <table style="width:100%;">
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="payBeVal">
                                                                    <xsl:call-template name="get_paybe">
                                                                        <xsl:with-param name="data" select="featureName"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$payBeVal='true'">
                                                                    <tr>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(featureName)"/>
                                                                        </td>
                                                                        <td style="width:60%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                            <xsl:call-template name="getCVDescription">
                                                                                <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(value)"/>
                                                                        </td>
                                                                        <td style="width:20%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                            <xsl:call-template name="get_PossibleRange">
                                                                                <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                    </tr>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
                                            <xsl:variable name="show_levbe">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                    <xsl:variable name="levBeVal">
                                                        <xsl:call-template name="get_levbe">
                                                            <xsl:with-param name="data" select="string(featureName)" />
                                                        </xsl:call-template>
                                                    </xsl:variable>
													<xsl:if test="$levBeVal='true'">
														1
													</xsl:if>
                                                </xsl:for-each>
                                            </xsl:variable>
                                            <xsl:if test="contains($show_levbe,'1')">
                                                <tr class="backclr">
                                                    <td width="20%;" class="BlackLabel padAll5">
																Leverage Behaviour
															</td>
                                                    <td width="80%;">
                                                        <table style="width:100%;">
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="levBeVal">
                                                                    <xsl:call-template name="get_levbe">
                                                                        <xsl:with-param name="data" select="featureName" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$levBeVal='true'">
                                                                    <tr>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(featureName)"/>
                                                                        </td>
                                                                        <td style="width:60%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                            <xsl:call-template name="getCVDescription">
                                                                                <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(value)"/>
                                                                        </td>
                                                                        <td style="width:20%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                            <xsl:call-template name="get_PossibleRange">
                                                                                <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                    </tr>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
											
                                            <xsl:variable name="show_credit">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                    <xsl:variable name="credVal">
                                                        <xsl:call-template name="get_credit">
                                                            <xsl:with-param name="data" select="string(featureName)"/>
                                                        </xsl:call-template>
                                                    </xsl:variable>
															<xsl:if test="$credVal='true'">
																1
															</xsl:if>
                                                </xsl:for-each>
                                            </xsl:variable>
                                            <xsl:if test="contains($show_credit,'1')">
                                                <!--<tr style="background-color: #f0f0f0!important;">-->
                                                <tr class="backclr">
                                                    <td width="20%;" class="BlackLabel padAll5">
																Credit Activity &amp; Vintage of Credit Activity
															</td>
                                                    <td width="80%;">
                                                        <table style="width:100%;">
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="credVal">
                                                                    <xsl:call-template name="get_credit">
                                                                        <xsl:with-param name="data" select="string(featureName)"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$credVal='true'">
                                                                    <tr>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(featureName)"/>
                                                                        </td>
                                                                        <td style="width:60%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                            <xsl:call-template name="getCVDescription">
                                                                                <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(value)"/>
                                                                        </td>
                                                                        <td style="width:20%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                            <xsl:call-template name="get_PossibleRange">
                                                                                <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                    </tr>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
                                            <xsl:variable name="show_credit_snap">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                     <xsl:variable name="credSnapVal">
                                                        <xsl:call-template name="get_credit_snap">
                                                            <xsl:with-param name="data" select="string(featureName)"/>
                                                        </xsl:call-template>
                                                    </xsl:variable>
														<xsl:if test="$credSnapVal='true'">
																1
														</xsl:if>
                                                </xsl:for-each>
                                            </xsl:variable>
                                            <xsl:if test="contains($show_credit_snap,'1')">
                                                <tr class="backclr">
                                                    <td width="20%;" class="BlackLabel padAll5">
																Credit Snapshot
															</td>
                                                    <td width="80%;">
                                                        <table style="width:100%;">
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="credSnapVal">
                                                                    <xsl:call-template name="get_credit_snap">
                                                                        <xsl:with-param name="data" select="featureName" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$credSnapVal='true'">
                                                                    <tr>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(featureName)"/>
                                                                        </td>
                                                                        <td style="width:60%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                            <xsl:call-template name="getCVDescription">
                                                                                <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(value)"/>
                                                                        </td>
                                                                        <td style="width:20%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                            <xsl:call-template name="get_PossibleRange">
                                                                                <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                    </tr>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
											
                                            <xsl:variable name="show_Demographic_Stability">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                    <xsl:variable name="demographicStability">
                                                        <xsl:call-template name="get_Demographic_Stability">
                                                            <xsl:with-param name="data" select="featureName"/>
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:if test="$demographicStability='true'">
															1
														 </xsl:if>
                                                </xsl:for-each>
                                            </xsl:variable>
                                            <xsl:if test="contains($show_Demographic_Stability,'1')">
                                                <tr class="backclr">
                                                    <td width="20%;" class="BlackLabel padAll5">
														  Demographic Stability
														</td>
                                                    <td width="80%;">
                                                        <table style="width:100%;">
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="demographic_Stability">
                                                                    <xsl:call-template name="get_Demographic_Stability">
                                                                        <xsl:with-param name="data" select="featureName"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$demographic_Stability='true'">
                                                                    <tr>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(featureName)"/>
                                                                        </td>
                                                                        <td style="width:60%;" class="BlackLabel padAll5">
                                                                            <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                            <xsl:call-template name="getCVDescription">
                                                                                <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                        <td style="width:10%;" class="BlackLabel padAll5">
                                                                            <xsl:value-of select="string(value)"/>
                                                                        </td>
                                                                        <td style="width:20%;" class="BlackLabel padAll5">
                                                                            <!-- <xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                            <xsl:call-template name="get_PossibleRange">
                                                                                <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                            </xsl:call-template>
                                                                        </td>
                                                                    </tr>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
                                            <xsl:variable name="show_others">
                                                <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                    <xsl:variable name="hideNTCVar">
                                                        <xsl:call-template name="hide_NTCvar">
                                                            <xsl:with-param name="data" select="featureName"/>
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:variable name="credSnapVal">
                                                        <xsl:call-template name="get_credit_snap">
                                                            <xsl:with-param name="data" select="featureName" />
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:variable name="credVal">
                                                        <xsl:call-template name="get_credit">
                                                            <xsl:with-param name="data" select="featureName" />
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:variable name="levelbe">
                                                        <xsl:call-template name="get_levbe">
                                                            <xsl:with-param name="data" select="featureName" />
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:variable name="paybe">
                                                        <xsl:call-template name="get_paybe">
                                                            <xsl:with-param name="data" select="featureName" />
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:variable name="demographic_Stability">
                                                        <xsl:call-template name="get_Demographic_Stability">
                                                            <xsl:with-param name="data" select="featureName"/>
                                                        </xsl:call-template>
                                                    </xsl:variable>
                                                    <xsl:if test="$hideNTCVar= 'true' ">
                                                        <xsl:if test="string($credSnapVal) = 'false' and string($credVal) = 'false' and string($levelbe) = 'false' and string($paybe) = 'false' and string($demographic_Stability) = 'false'">
																1
															</xsl:if>
															
                                                    </xsl:if>
                                                </xsl:for-each>
                                            </xsl:variable>
                                            <xsl:if test="contains($show_others,'1')">
                                                <!--<tr style="background-color: #f0f0f0!important;" id="other">-->
                                                <tr class="backclr">
                                                    <td width="20%;" class="BlackLabel padAll5">
																	Others
																</td>
                                                    <td width="80%;">
                                                        <table style="width:100%;">	
                                                            <xsl:for-each select="Root/root/consumerCreditData/item/bureauCharacteristics/item">
                                                                <xsl:variable name="varNTC">
                                                                    <xsl:call-template name="hide_NTCvar">
                                                                        <xsl:with-param name="data" select="string(featureName)"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:variable name="credSnapVal">
                                                                    <xsl:call-template name="get_credit_snap">
                                                                        <xsl:with-param name="data" select="string(featureName)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:variable name="credVal">
                                                                    <xsl:call-template name="get_credit">
                                                                        <xsl:with-param name="data" select="string(featureName)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:variable name="levelbe">
                                                                    <xsl:call-template name="get_levbe">
                                                                        <xsl:with-param name="data" select="string(featureName)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:variable name="paybe">
                                                                    <xsl:call-template name="get_paybe">
                                                                        <xsl:with-param name="data" select="string(featureName)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:variable name="demographic_Stability">
                                                                    <xsl:call-template name="get_Demographic_Stability">
                                                                        <xsl:with-param name="data" select="string(featureName)"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:if test="$varNTC='true'">
                                                                    <xsl:variable name="others">
                                                                        <xsl:choose>
                                                                            <xsl:when test="$credSnapVal='true' or $credVal='true' or $levelbe='true' or $paybe='true' or $demographic_Stability='true'">
																							True
																						</xsl:when>
                                                                            <xsl:otherwise>
																							False
																						</xsl:otherwise>
                                                                        </xsl:choose>
                                                                    </xsl:variable>
                                                                    <xsl:if test="contains($others,'False')">
                                                                        <tr>
                                                                            <td style="width:10%;" class="BlackLabel padAll5">
                                                                                <xsl:value-of select="string(featureName)"/>
                                                                            </td>
                                                                            <td style="width:60%;" class="BlackLabel padAll5">
                                                                                <!--<xsl:value-of select="usr:getCVDescription(string(featureName))"/>-->
                                                                                <xsl:call-template name="getCVDescription">
                                                                                    <xsl:with-param name="cvId" select="string(featureName)"/>
                                                                                </xsl:call-template>
                                                                            </td>
                                                                            <td style="width:10%;" class="BlackLabel padAll5">
                                                                                <xsl:value-of select="string(value)"/>
                                                                            </td>
                                                                            <td style="width:20%;" class="BlackLabel padAll5">
                                                                                <!--<xsl:value-of select="usr:get_PossibleRange(string(featureName))"/>-->
                                                                                <xsl:call-template name="get_PossibleRange">
                                                                                    <xsl:with-param name="rangeId" select="string(featureName)"/>
                                                                                </xsl:call-template>
                                                                            </td>
                                                                        </tr>
                                                                    </xsl:if>
                                                                </xsl:if>
                                                            </xsl:for-each>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </xsl:if>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                        </xsl:if>
                        <!-- Credit Vsion Segement End -->
						
                        <!-- Consumer Score Details End-->
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- Consumer Score Range Details Start-->
                        <xsl:for-each select="Root/root/consumerCreditData/item/scores/item">
                            <xsl:if test="((scoreCardName != '02') and (scoreCardName != '11') and (scoreCardName != '12') and (scoreCardName != '13') and (scoreCardName != '14') and (scoreCardName != '15') and (scoreCardName != '16') and (scoreCardName != '17'))">
                                <tr>
                                    <td>
                                        <table width="1000" style="background-color: #ededed!important;padding: 5px;" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="800px" class="conslabelBlueBig">
														POSSIBLE RANGE FOR 
                                                    
                                                    
                                                    <xsl:choose>
                                                        <xsl:when test="scoreCardName = '04'">
																CIBIL TRANSUNION SCORE 
                                                            
                                                            
                                                            <br> VERSION 2.0</br>
                                                        </xsl:when>
                                                        <xsl:when test="scoreCardName = '01'">
																CIBIL TRANSUNION SCORE 
                                                            
                                                            
                                                            <br> VERSION 1.0</br>
                                                        </xsl:when>
                                                        <xsl:when test="scoreCardName = '08'">
																CREDITVISION® SCORE
															</xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="200px"></td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
                                                    <xsl:choose>
                                                        <xsl:when test="scoreCardName = '08'">
																Consumer with at least one trade on the bureau in last 36 months
															</xsl:when>
                                                        <xsl:otherwise>
																Consumers with more than 6 months credit history*
															</xsl:otherwise>
                                                    </xsl:choose>
                                                    <!--Consumers with more than 6 months credit history*-->

                                                </td>
                                                <xsl:if test="((scoreCardName != '11') and (scoreCardName != '12') and (scoreCardName != '13') and (scoreCardName) and (scoreCardName != '15') and (scoreCardName != '16') and (scoreCardName != '17'))">
                                                    <td width="400px" class="RedLabel">: 300 (high risk) to 900 (low risk)</td>
                                                </xsl:if>
                                            </tr>
                                            <xsl:if test="((scoreCardName != '08') and (scoreCardName != '11') and (scoreCardName != '12') and (scoreCardName != '13') and (scoreCardName != '14') and (scoreCardName != '15') and (scoreCardName != '16') and (scoreCardName != '17'))">
                                                <tr>
                                                    <td width="600px" class="BlackLabel">
															Consumers having less than 6 months credit history*
														</td>
                                                    <td width="400px" class="RedLabel">
                                                        <xsl:choose>
                                                            <xsl:when test="scoreCardName = '04'">
																	: 1 (high risk) to 5 (low risk)
																</xsl:when>
                                                            <xsl:when test="scoreCardName = '01'">
																	: 0
																</xsl:when>
                                                            <xsl:when test="scoreCardName = '08'">
																	: 0
																</xsl:when>
                                                            <xsl:otherwise>
																	:" "
																</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                </tr>
                                            </xsl:if>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
                                                    <xsl:choose>
                                                        <xsl:when test="scoreCardName = '08'">
																Consumer not in CIBIL database or history older than 36 months
															</xsl:when>
                                                        <xsl:otherwise>
																Consumers not in CIBIL database or with insufficient information for scoring*
															</xsl:otherwise>
                                                    </xsl:choose>
                                                    <!--Consumers not in CIBIL database or with insufficient information for scoring*-->

                                                
                                                </td>
                                                <td width="400px" class="RedLabel">: -1</td>
                                            </tr>
                                            <tr>
                                                <td colspan="4" height="8px"></td>
                                            </tr>
                                            <tr>
                                                <td colspan="4" height="8px"></td>
                                            </tr>
                                            <tr>
                                                <td width="1000px" class="BlackLabel">
                                                    <xsl:if test="((scoreCardName != '11') and (scoreCardName != '12') and (scoreCardName != '13') and (scoreCardName != '14') and (scoreCardName != '15') and (scoreCardName != '16') and (scoreCardName != '17'))">
                                                        <xsl:choose>
                                                            <xsl:when test="scoreCardName = '08'">
																	* At least one tradeline with information updated in last 36 months is required.
																</xsl:when>
                                                            <xsl:otherwise>
																	* At least one tradeline with information updated in last 24 months is required.In case of error in scoring a value of 
                                                                
                                                                
                                                                <span class="RedLabel">'0'</span> is returned.
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </xsl:if>
                                                    <!--* At least one tradeline with information updated in last 24 months is required.In case of error in scoring a value of <span class="RedLabel">'0'</span> is returned.-->

                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                            <xsl:if test="scoreCardName = '16'">
                                <tr>
                                    <td>
                                        <table width="1000" style="background-color: #ededed!important;padding: 5px;" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="800px" class="conslabelBlueBig">
											POSSIBLE RANGE FOR 
                                                    
                                                    
                                                    <xsl:choose>
                                                        <xsl:when test="scoreCardName = '16'">
												CREDITVISION® NEW TO CREDIT SCORE
											  </xsl:when>
                                                        <xsl:otherwise>
											  </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="200px"></td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
											Consumer not in CIBIL database or history older than 36 months
										  </td>
                                                <td width="400px" class="RedLabel">: Score range is between 100 and 200</td>
                                            </tr>
                                            <tr>
                                                <td width="1000px" class="BlackLabel">

										  </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                            <xsl:if test="scoreCardName = '02'">
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td>
                                        <table width="1000" style="background-color: #ededed!important;padding: 5px" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="600px" class="conslabelBlueBig">
														POSSIBLE RANGE FOR 
                                                    
                                                    
                                                    <xsl:choose>
                                                        <xsl:when test="scoreCardName = '02'">
																PERSONAL LOAN SCORE
															</xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="400px"></td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
														Consumers with more than 1 month credit history*
													</td>
                                                <td width="400px" class="RedLabel">: 300 (high risk) to 900 (low risk)</td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
														Consumers not in CIBIL database or with insufficient information for scoring*
													</td>
                                                <td width="400px" class="RedLabel">: -1</td>
                                            </tr>
                                            <tr>
                                                <td colspan="4" height="8px"></td>
                                            </tr>
                                            <tr>
                                                <td colspan="4" height="8px"></td>
                                            </tr>
                                            <tr>
                                                <td width="1000px" class="BlackLabel">
														* At least one tradeline with information updated in last 24 months is required.In case of error in scoring a value of 
                                                    
                                                    
                                                    <span color="red">'0'</span> is returned.
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                            <xsl:if test="((scoreCardName = '11') or (scoreCardName = '14'))">
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td>
                                        <table width="1000" style="background-color: #ededed!important;padding: 5px;" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="800px" class="conslabelBlueBig">
														POSSIBLE RANGE FOR 
                                                    
                                                    
                                                    <xsl:choose>
                                                        <xsl:when test="((scoreCardName = '11') or (scoreCardName = '12') or (scoreCardName = '13') or (scoreCardName = '14') or (scoreCardName = '15') or (scoreCardName = '16') or (scoreCardName = '17'))">
																ESTIMATED INCOME BAND
															</xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="200px"></td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
                                                    <xsl:choose>
                                                        <xsl:when test="((scoreCardName = '11') or (scoreCardName = '12') or (scoreCardName = '13') or (scoreCardName = '14') or (scoreCardName = '15') or (scoreCardName = '16') or (scoreCardName = '17'))">
                                                            <table  width="60%" style="background-color: #ededed!important;padding: 5px;text-align: left;" border="0" cellpadding="0" cellspacing="0">
                                                                <thead class="conslabelBlueBig" style="color:#00a7d4;">
                                                                    <tr>
                                                                        <th>Estimated Income Band</th>
                                                                        <th>Income Band (INR)</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig"></td>
                                                                        <td class="conslabelBlueBig"></td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">1</td>
                                                                        <td class="conslabelBlueBig">&lt;360k </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">2</td>
                                                                        <td  class="conslabelBlueBig">[360k-480k] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td  class="conslabelBlueBig">3</td>
                                                                        <td  class="conslabelBlueBig">[480k-600k]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">4</td>
                                                                        <td class="conslabelBlueBig">[600k-720k] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">5</td>
                                                                        <td  class="conslabelBlueBig">[720k-840k]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">6</td>
                                                                        <td  class="conslabelBlueBig">[840k-1.2m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td  class="conslabelBlueBig">7</td>
                                                                        <td  class="conslabelBlueBig">[1.2m-1.5m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">8</td>
                                                                        <td  class="conslabelBlueBig">[1.5m-2m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">9</td>
                                                                        <td  class="conslabelBlueBig">[2m-2.5m] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">10</td>
                                                                        <td class="conslabelBlueBig"> &gt;=2.5m</td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="800px" class="BlackLabel">
													  Note – For subjects having not enough information on bureau, value = 000-1 is returned in output string.
													  </td>
                                                <td width="200px"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                            <xsl:if test="((scoreCardName = '12') or (scoreCardName = '13') or (scoreCardName = '15') or (scoreCardName = '17'))">
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                </tr>
                                <tr>
                                    <td>
                                        <table width="1000" style="background-color: #ededed!important;padding: 5px;" border="0" align="right" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td width="800px" class="conslabelBlueBig">
														POSSIBLE RANGE FOR 
                                                    
                                                    
                                                    <xsl:choose>
                                                        <xsl:when test="((scoreCardName = '12') or (scoreCardName = '13')or (scoreCardName = '15') or (scoreCardName = '17'))">
																ESTIMATED INCOME BAND
															</xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="200px"></td>
                                            </tr>
                                            <tr>
                                                <td width="600px" class="BlackLabel">
                                                    <xsl:choose>
                                                        <xsl:when test="((scoreCardName = '12') or (scoreCardName = '13') or (scoreCardName = '15') or (scoreCardName = '17'))">
                                                            <table  width="60%" style="background-color: #ededed!important;padding: 5px;text-align: left;" border="0" cellpadding="0" cellspacing="0">
                                                                <thead class="conslabelBlueBig" style="color:#00a7d4;">
                                                                    <tr>
                                                                        <th>Estimated Income Band</th>
                                                                        <th>Income Band (INR)</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig"></td>
                                                                        <td class="conslabelBlueBig"></td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">1</td>
                                                                        <td class="conslabelBlueBig">&lt;240k </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">2</td>
                                                                        <td  class="conslabelBlueBig">[240k-480k] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td  class="conslabelBlueBig">3</td>
                                                                        <td  class="conslabelBlueBig">[480k-720k]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">4</td>
                                                                        <td class="conslabelBlueBig">[720k-960k] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">5</td>
                                                                        <td  class="conslabelBlueBig">[960k-1.2m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">6</td>
                                                                        <td  class="conslabelBlueBig">[1.2m-1.5m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td  class="conslabelBlueBig">7</td>
                                                                        <td  class="conslabelBlueBig">[1.5m-1.8m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">8</td>
                                                                        <td  class="conslabelBlueBig">[1.8m-2.1m]</td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">9</td>
                                                                        <td  class="conslabelBlueBig">[2.1m-2.4m] </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td class="conslabelBlueBig">10</td>
                                                                        <td class="conslabelBlueBig"> &gt;=2.4m</td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </xsl:when>
                                                        <xsl:otherwise>
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="800px" class="BlackLabel">
													  Note – For subjects having not enough information on bureau, value = 000-1 is returned in output string.
													  </td>
                                                <td width="200px"></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <!-- Consumer Score Range Details end-->
                        <tr>
                            <td colspan="4" height="8px"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px"></td>
                        </tr>
                        <!-- Identifiation segment starts-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="300px" class="constitleGreyBig">IDENTIFICATION(S):</td>
                                        <td width="330px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:if test="Root/root/consumerCreditData/item/ids/item[1] !=''">
                                        <tr>
                                            <td width="250px" class="BlueLabel">IDENTIFICATION TYPE</td>
                                            <td width="250px" class="BlueLabel">IDENTIFICATION NUMBER</td>
                                            <td width="250px" class="BlueLabel">ISSUE DATE</td>
                                            <td width="250px" class="BlueLabel">EXPIRATION DATE</td>
                                        </tr>
                                        <xsl:for-each select="Root/root/consumerCreditData/item/ids/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="250px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="idType = '01'">
																INCOME TAX ID NUMBER (PAN)
															</xsl:when>
                                                        <xsl:when test="idType = '02'">
																PASSPORT NUMBER
															</xsl:when>
                                                        <xsl:when test="idType = '03'">
																VOTER ID
															</xsl:when>
                                                        <xsl:when test="idType = '04'">
																DRIVER'S LICENSE NUMBER
															</xsl:when>
                                                        <xsl:when test="idType = '05'">
																RATION CARD NUMBER
															</xsl:when>
                                                        <xsl:when test="idType = '06'">
																UNIVERSAL ID NUMBER (UID)
															</xsl:when>
														<xsl:when test="idType = '09'">
																CKYC
															</xsl:when>
														<xsl:when test="idType = '10'">
																NREGA CARD NUMBER
														</xsl:when>
                                                        <xsl:otherwise>
																NOT CLASSIFIED
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="250px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="idType = '06'">
																NOT DISCLOSED
															</xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:value-of select="idNumber"></xsl:value-of>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="250px" class="BlackLabel padAll5">
                                                    <!--<xsl:value-of select="usr:formatDate(string(IssueDate))"/>-->
                                                    <xsl:call-template name="formatDate">
                                                        <xsl:with-param name="inpDate" select="string(IssueDate)"/>
                                                    </xsl:call-template>
                                                </td>
                                                <td width="250px" class="BlackLabel padAll5">
                                                    <!--<xsl:value-of select="usr:formatDate(string(ExpirationDate))"/>-->
                                                    <xsl:call-template name="formatDate">
                                                        <xsl:with-param name="inpDate" select="string(ExpirationDate)"/>
                                                    </xsl:call-template>
                                                </td>
                                            </tr>
                                        </xsl:for-each>
                                    </xsl:if>
                                </table>
                            </td>
                        </tr>
                        <!-- identification segment end-->
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- telephone segment starts-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="300px" class="constitleGreyBig">TELEPHONE(S):</td>
                                        <td width="330px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:variable name="MissingTelephone" select="Root/root/controlData/errorResponseArray/errorMessage"/>
                                    <xsl:value-of select="$MissingTelephone"/>
                                    <xsl:if test="Root/root/consumerCreditData/item/telephones/item[1] !=''">
                                        <tr>
                                            <td width="300px" class="BlueLabel">TELEPHONE TYPE</td>
                                            <td width="330px" class="BlueLabel">TELEPHONE NUMBER</td>
                                            <td width="370px" class="BlueLabel">TELEPHONE EXTENSION</td>
                                        </tr>
                                        <xsl:for-each select="Root/root/consumerCreditData/item/telephones/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="300px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="telephoneType = '01'">
																MOBILE PHONE
																
                                                            
                                                            
                                                            <xsl:if test="enquiryEnriched = 'Y'">
                                                                <sup>(e)</sup>
                                                            </xsl:if>
                                                        </xsl:when>
                                                        <xsl:when test="telephoneType = '02'">
																HOME PHONE
																
                                                            
                                                            
                                                            <xsl:if test="enquiryEnriched = 'Y'">
                                                                <sup>(e)</sup>
                                                            </xsl:if>
                                                        </xsl:when>
                                                        <xsl:when test="telephoneType = '03'">
																OFFICE PHONE
																
                                                            
                                                            
                                                            <xsl:if test="enquiryEnriched = 'Y'">
                                                                <sup>(e)</sup>
                                                            </xsl:if>
                                                        </xsl:when>
                                                        <xsl:otherwise>
																NOT CLASSIFIED
																
                                                            
                                                            
                                                            <xsl:if test="enquiryEnriched= 'Y'">
                                                                <sup>(e)</sup>
                                                            </xsl:if>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="330px" class="BlackLabel padAll5">
                                                    <xsl:value-of select="telephoneNumber"/>
                                                </td>
                                                <td width="370px" class="BlackLabel padAll5">
                                                    <xsl:value-of select="TelephoneExtension"/>
                                                </td>
                                            </tr>
                                        </xsl:for-each>
                                    </xsl:if>
                                </table>
                            </td>
                        </tr>
                        <!-- telephone segment end-->
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- email segment starts-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="300px" class="constitleGreyBig">EMAIL CONTACT(S):</td>
                                        <td width="330px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:if test="Root/root/consumerCreditData/item/emails/item[1] != ''">
                                        <tr>
                                            <td width="300px" class="BlueLabel">EMAIL ADDRESS</td>
                                            <td width="330px" class="BlueLabel"></td>
                                            <td width="370px" class="BlueLabel"></td>
                                        </tr>
                                        <xsl:for-each select="Root/root/consumerCreditData/item/emails/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="300px" class="BlackLabel padAll5">
                                                    <xsl:value-of select="emailID"/>
                                                </td>
                                                <td width="330px" class="BlackLabel padAll5">
													</td>
                                                <td width="370px" class="BlackLabel padAll5"></td>
                                            </tr>
                                        </xsl:for-each>
                                    </xsl:if>
                                </table>
                            </td>
                        </tr>
                        <!-- email segment end-->
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- address segment starts-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="300px" class="constitleGreyBig">ADDRESS(ES):</td>
                                        <td width="330px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:if test="Root/root/consumerCreditData/item/addresses/item[1] != ''">
                                        <xsl:for-each select="Root/root/consumerCreditData/item/addresses/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="975px" colspan="3" class="BlueLabelBigger2 padAll5">
														ADDRESS

                                                    <xsl:if test="enquiryEnriched = 'Y'">
                                                        <sup style="text-transform:lowercase;">(e)</sup>
                                                    </xsl:if>
														:
                                                    <span class="conslabelBlackBig padAll5">
                                                        <xsl:if test="line1 != ''">
                                                            <xsl:value-of select="line1"/>
                                                        </xsl:if>
                                                        <xsl:if test="line2 != ''">
																,<xsl:value-of select="line2"/>
                                                        </xsl:if>
                                                        <xsl:if test="line3 != ''">
																,<xsl:value-of select="line3"/>
                                                        </xsl:if>
                                                        <xsl:if test="line4 != ''">
																,<xsl:value-of select="line4"/>
                                                        </xsl:if>
                                                        <xsl:if test="line5 != ''">
																,<xsl:value-of select="line5"/>
                                                        </xsl:if>
                                                        <xsl:if test="stateCode != ''">
																,
															<xsl:call-template name="GetState">
                                                                <xsl:with-param name="stCode" select="string(stateCode)"/>
                                                            </xsl:call-template>
                                                        </xsl:if>
                                                        <xsl:if test="pinCode != ''">
																,<xsl:value-of select="pinCode"/>
                                                        </xsl:if>
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="300px" class="conslabelBlackBig padAll5">
                                                    <span class="BlueLabelBigger2">CATEGORY:</span>
                                                    <xsl:if test="addressCategory = '01'">
															Permanent Address
														</xsl:if>
                                                    <xsl:if test="addressCategory = '02'">
															Residence Address
														</xsl:if>
                                                    <xsl:if test="addressCategory = '03'">
															Office Address
														</xsl:if>
                                                    <xsl:if test="addressCategory = '04'">
															Not Categorized
														</xsl:if>
													<xsl:if test="addressCategory = '05'">
														Mortgage Property address
													</xsl:if>
                                                </td>
                                                <td width="330px" class="conslabelBlackBig padAll5">
                                                    <span class="BlueLabelBigger2">RESIDENCE CODE:</span>
                                                    <xsl:choose>
                                                        <xsl:when test="residenceCode = '01'">
																Owned
															</xsl:when>
                                                        <xsl:when test="residenceCode = '02'">
																Rented
															</xsl:when>
															
                                                        <xsl:otherwise>
																<xsl:text>NA</xsl:text>					
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="370px">
                                                    <span class="BlueLabelBigger2">DATE REPORTED:</span>
                                                    <span class="conslabelBlackBig padAll5">                                                        
                                                        <xsl:call-template name="formatDate">
                                                            <xsl:with-param name="inpDate" select="string(dateReported)"/>
                                                        </xsl:call-template>
                                                    </span>
                                                </td>
                                            </tr>
                                        </xsl:for-each>
                                    </xsl:if>
                                </table>
                            </td>
                        </tr>
                        <!-- address segment end-->
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- employment segment starts-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="330px" class="constitleGreyBig">EMPLOYMENT INFORMATION:</td>
                                        <td width="300px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:if test="Root/root/consumerCreditData/item/employment/item[1] != ''">
                                        <tr>
                                            <td width="165px" class="BlueLabel">ACCOUNT TYPE</td>
                                            <td width="165px" class="BlueLabel">DATE REPORTED</td>
                                            <td width="165px" class="BlueLabel">OCCUPATION CODE</td>
                                            <td width="165px" class="BlueLabel">INCOME</td>
                                            <td width="165px" class="BlueLabel">NET / GROSS INCOME INDICATOR</td>
                                            <td width="175px" class="BlueLabel">MONTHLY / ANNUAL INCOME INDICATOR</td>
                                        </tr>
                                        <xsl:for-each select="Root/root/consumerCreditData/item/employment/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="165px" class="BlackLabel padAll5">
                                                    <!-- TODO: Complete script to match the account type value -->
                                                    <!--<xsl:value-of select="usr:getAccountType(string(accountType))"/>-->
                                                    <xsl:call-template name="getAccountType">
                                                        <xsl:with-param name="id" select="string(accountType)"/>
                                                    </xsl:call-template>
                                                </td>
                                                <td width="165px" class="BlackLabel padAll5">
                                                    <!-- TODO: Complete script to form date properly in dd-mm-yyyy -->
                                                    <!--<xsl:value-of select="usr:formatDate(string(dateReported))"/>-->
                                                    <xsl:call-template name="formatDate">
                                                        <xsl:with-param name="inpDate" select="string(dateReported)"/>
                                                    </xsl:call-template>
                                                </td>
                                                <td width="165px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="occupationCode = '01'">
																Salaried
															</xsl:when>
                                                        <xsl:when test="occupationCode = '02'">
																Self Employed Professional
															</xsl:when>
                                                        <xsl:when test="occupationCode = '03'">
																Self Employed
															</xsl:when>
                                                        <xsl:when test="occupationCode = '04'">
																Others
															</xsl:when>
                                                        <xsl:otherwise>

															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="165px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="Income != ''">
                                                            <!--<xsl:value-of select="format-number(Income, '#,###')"/>-->
                                                            <xsl:call-template name="AmountCommaSeperator">
                                                                <xsl:with-param name="Amount" select="Income"></xsl:with-param>
                                                            </xsl:call-template>
                                                        </xsl:when>
                                                        <xsl:otherwise>Not Available</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="165px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="NetGrossIndicator = 'G'">
																Gross Income
															</xsl:when>
                                                        <xsl:when test="NetGrossIndicator = 'N'">
																Net Income
															</xsl:when>
                                                        <xsl:otherwise>
																Not Available
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td width="175px" class="BlackLabel padAll5">
                                                    <xsl:choose>
                                                        <xsl:when test="MonthlyAnnualIndicator = 'M'">
																Monthly
															</xsl:when>
                                                        <xsl:when test="MonthlyAnnualIndicator = 'A'">
																Annual
															</xsl:when>
                                                        <xsl:otherwise>
																Not Available
															</xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                            </tr>
                                        </xsl:for-each>
                                    </xsl:if>
                                    <xsl:if test="(Root/root/CreditReport/EmploymentSegment/ErrorCode!= '') or (Root/root/CreditReport/EmploymentSegment/cibilRemarksCode != '')">
                                        <tr>
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <xsl:if test="$oddRow">
                                                <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                            </xsl:if>
                                            <td  width="1000px" class="greyallborder15" colspan="6">
                                                <table>
                                                    <tr>
                                                        <td class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">EMPLOYMENT INFORMATION UNDER DISPUTE:</span>
                                                            <!--<xsl:value-of select="usr:ToUpper(usr:getEmploymentDisputeDesc(string(Root/root/CreditReport/EmploymentSegment/ErrorCode)))"/>-->
                                                            <xsl:variable name="empDisputeDesc">
                                                                <xsl:call-template name="getEmploymentDisputeDesc">
                                                                    <xsl:with-param name="empDisputeId" select="string(Root/root/CreditReport/EmploymentSegment/ErrorCode)"/>
                                                                </xsl:call-template>
                                                            </xsl:variable>
                                                            <xsl:call-template name="ToUpper">
                                                                <xsl:with-param name="data" select="$empDisputeDesc"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <xsl:if test="$oddRow">
                                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                        </xsl:if>
                                                        <td colspan="6" height="8px"></td>
                                                    </tr>
                                                    <xsl:if test="Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode1 != ''">
                                                        <tr>
                                                            <td class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">DISPUTE REMARKS:</span>
                                                                <!--<xsl:value-of select="usr:ToUpper(usr:getDisputeRemarkCodeDesc(string(Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode1)))"/>-->
                                                                <xsl:variable name="empDisputeRemark1">
                                                                    <xsl:call-template name="getDisputeRemarkCodeDesc">
                                                                        <xsl:with-param name="id"
																				select="string(Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode1)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:call-template name="ToUpper">
                                                                    <xsl:with-param name="data" select="$empDisputeRemark1" />
                                                                </xsl:call-template>
                                                            </td>
                                                        </tr>
                                                    </xsl:if>
                                                    <xsl:if test="Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode2 != ''">
                                                        <tr>
                                                            <td class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">DISPUTE REMARKS #2:</span>
                                                                <!--<xsl:value-of select="usr:ToUpper(usr:getDisputeRemarkCodeDesc(string(Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode2)))"/>-->
                                                                <xsl:variable name="empDisputeRemark2">
                                                                    <xsl:call-template name="getDisputeRemarkCodeDesc">
                                                                        <xsl:with-param name="id"
																				select="string(Root/root/CreditReport/EmploymentSegment/ErrorDisputeRemarksCode2)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:call-template name="ToUpper">
                                                                    <xsl:with-param name="data" select="$empDisputeRemark2" />
                                                                </xsl:call-template>
                                                            </td>
                                                        </tr>
                                                    </xsl:if>
                                                    <xsl:if test="Root/root/CreditReport/EmploymentSegment/cibilRemarksCode != ''">
                                                        <tr>
                                                            <td class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">CIBIL REMARKS:</span>
                                                                <!--<xsl:value-of select="usr:ToUpper(usr:getRemarkCodeDesc(string(Root/root/CreditReport/EmploymentSegment/cibilRemarksCode)))"/>-->
                                                                <xsl:variable name="empDisputeRemarkDesc">
                                                                    <xsl:call-template name="getRemarkCodeDesc">
                                                                        <xsl:with-param name="id"
																				select="string(Root/root/CreditReport/EmploymentSegment/cibilRemarksCode)" />
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:call-template name="ToUpper">
                                                                    <xsl:with-param name="data" select="$empDisputeRemarkDesc" />
                                                                </xsl:call-template>
                                                            </td>
                                                        </tr>
                                                    </xsl:if>
                                                    <xsl:if test="Root/root/CreditReport/EmploymentSegment/DateOfEntryForcibilRemarksCode != ''">
                                                        <tr>
                                                            <td class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">DATE ENTERED:</span>
                                                                <!--<xsl:value-of select="usr:formatDate(string(Root/root/CreditReport/EmploymentSegment/DateOfEntryForcibilRemarksCode))"/>-->
                                                                <xsl:call-template name="formatDate">
                                                                    <xsl:with-param name="inpDate" select="string(Root/root/CreditReport/EmploymentSegment/DateOfEntryForcibilRemarksCode)" />
                                                                </xsl:call-template>
                                                            </td>
                                                        </tr>
                                                    </xsl:if>
                                                </table>
                                            </td>
                                        </tr>
                                    </xsl:if>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- Summary segment start-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="330px" class="constitleGreyBig">SUMMARY:</td>
                                        <td width="300px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <tr>
                                        <td width="330px" class="BlueLabelBigger3">ACCOUNT(S)</td>
                                        <td width="300px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <tr>
                                        <td width="200px" class="BlueLabel">ACCOUNT TYPE</td>
                                        <td width="200px" class="BlueLabel">ACCOUNTS</td>
                                        <td width="200px" class="BlueLabel">ADVANCES</td>
                                        <td width="200px" class="BlueLabel">BALANCES</td>
                                        <td width="200px" class="BlueLabel" colspan="2">DATE OPENED</td>
                                    </tr>
                                    <tr>
                                        <xsl:variable name="oddRow" select="position() mod 2" />
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="200px" class="BlackLabel padAll5">All Accounts</td>
                                        <td width="200px" class="BlackLabel padAll5" style="border-bottom:1.2px solid #cecece">
                                            <span class="GreyItalicLabel">TOTAL:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/totalAccounts !=''">
                                                    <!--<xsl:value-of select="count(Root/root/CreditReport/Account)" />-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/totalAccounts">
													</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="200px" class="BlackLabel padAll5">
                                            <span class="GreyItalicLabel">HIGH CR/SANC. AMT:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/highCreditAmount !=''">
                                                    <!--<xsl:value-of select="format-number(sum(Root/root/CreditReport/Account/Account_NonSummary_Segment_Fields/HighCreditOrSanctionedAmount), '##,##,##,###')" />-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/highCreditAmount">
															</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise></xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="200px" class="BlackLabel padAll5" style="border-bottom:1.2px solid #cecece">
                                            <span class="GreyItalicLabel">CURRENT:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/currentBalance != ''">
                                                    <!--<xsl:value-of select="format-number(sum(Root/root/CreditReport/Account/Account_NonSummary_Segment_Fields/CurrentBalance), '#,###')" />-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/currentBalance">
															</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise></xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="200px" colspan="2" class="BlackLabel padAll5" style="border-bottom:1.2px solid #cecece">
                                            <span class="GreyItalicLabel">RECENT:</span>
                                            <!--<xsl:value-of select="usr:formatDate(string(Root/root/consumerSummaryData/accountSummary/recentDateOpened))"/>-->
                                            <xsl:call-template name="formatDate">
                                                <xsl:with-param name="inpDate" select="string(string(Root/root/consumerSummaryData/accountSummary/recentDateOpened))"/>
                                            </xsl:call-template>
                                        </td>
                                    </tr>
                                    <tr>
                                        <xsl:variable name="oddRow" select="position() mod 2" />
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="200px" class="BlackLabel padAll5"></td>
                                        <td width="200px" class="BlackLabel padAll5">
                                            <span class="GreyItalicLabel">OVERDUE:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/overdueAccounts !=''">
                                                    <!--<xsl:value-of select="count(Root/root/CreditReport/Account/Account_NonSummary_Segment_Fields/AmountOverdue)" />-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/overdueAccounts">
													</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="200px" class="BlackLabel padAll5">

											</td>
                                        <td width="200px" class="BlackLabel padAll5">
                                            <span class="GreyItalicLabel">OVERDUE:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/overdueBalance">
                                                    <!--<xsl:value-of select="format-number(sum(Root/root/CreditReport/Account/Account_NonSummary_Segment_Fields/AmountOverdue), '#,###')" />-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/overdueBalance">
															</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise></xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="200px" colspan="2" class="BlackLabel padAll5">
                                            <span class="GreyItalicLabel">OLDEST:</span>
                                            <!--<xsl:value-of select="usr:formatDate(string(Root/root/consumerSummaryData/accountSummary/oldestDataOpened))"/>-->
                                            <xsl:call-template name="formatDate">
                                                <xsl:with-param name="inpDate" select="string(Root/root/consumerSummaryData/accountSummary/oldestDateOpened)"/>
                                            </xsl:call-template>
                                        </td>
                                    </tr>
                                    <tr>
                                        <xsl:variable name="oddRow" select="position() mod 2" />
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="200px" class="BlackLabel padAll5"></td>
                                        <td width="200px" class="BlackLabel padAll5">
                                            <span class="GreyItalicLabel">ZERO-BALANCE:</span>
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/accountSummary/zeroBalanceAccounts !=''">
                                                    <!--<xsl:value-of select="count($current-group)"/>-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="Root/root/consumerSummaryData/accountSummary/zeroBalanceAccounts">
													</xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
										
										
										
                                        <td width="200px" class="BlackLabel padAll5">
											</td>
                                        <td width="200px" class="BlackLabel padAll5">
											</td>
                                        <td width="200px" colspan="2" class="BlackLabel padAll5">
											</td>
                                    </tr>
                                    <tr>
                                        <td width="330px" class="BlueLabelBigger3">ENQUIRIES</td>
                                        <td width="300px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <tr>
                                        <td width="165px" class="BlueLabel">ENQUIRY PURPOSE</td>
                                        <td width="165px" class="BlueLabel">TOTAL</td>
                                        <td width="165px" class="BlueLabel">PAST 30 DAYS</td>
                                        <td width="165px" class="BlueLabel">PAST 12 MONTHS</td>
                                        <td width="165px" class="BlueLabel">PAST 24 MONTHS</td>
                                        <td width="165px" class="BlueLabel">RECENT</td>
                                    </tr>
                                    <tr>
                                        <xsl:variable name="oddRow" select="position() mod 2" />
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="165px" class="BlackLabel padAll5">All Enquiries</td>
                                        <td width="165px" class="BlackLabel padAll5">
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/inquirySummary/totalInquiry !=''">
                                                    <xsl:value-of select="Root/root/consumerSummaryData/inquirySummary/totalInquiry" />
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="165px" class="BlackLabel padAll5">
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/inquirySummary/inquiryPast30Days !=''">
                                                    <xsl:value-of select="Root/root/consumerSummaryData/inquirySummary/inquiryPast30Days" />
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="165px" class="BlackLabel padAll5">
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/inquirySummary/inquiryPast12Months !=''">
                                                    <xsl:value-of select="Root/root/consumerSummaryData/inquirySummary/inquiryPast12Months" />
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="165px" class="BlackLabel padAll5">
                                            <xsl:choose>
                                                <xsl:when test="Root/root/consumerSummaryData/inquirySummary/inquiryPast24Months !=''">
                                                    <xsl:value-of select="Root/root/consumerSummaryData/inquirySummary/inquiryPast24Months" />
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="0"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                        <td width="165px" class="BlackLabel padAll5">
                                            <!--<xsl:value-of select="usr:formatDate(string(Root/root/consumerSummaryData/inquirySummary/recentInquiryDate))"/>-->
                                            <xsl:call-template name="formatDate">
                                                <xsl:with-param name="inpDate" select="string(Root/root/consumerSummaryData/inquirySummary/recentInquiryDate)"/>
                                            </xsl:call-template>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <!-- Summary segment end-->
                        <tr>
						
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <tr>
                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                        </tr>
                        <!-- Account segment start-->
                        <tr>
                            <td>
                                <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="330px" class="constitleGreyBig">ACCOUNT(S):</td>
                                        <td width="300px"></td>
                                        <td width="370px"></td>
                                    </tr>
                                    <xsl:if test="Root/root/consumerCreditData/item/accounts != ''">
                                        <xsl:for-each select="Root/root/consumerCreditData/item/accounts/item">
                                            <xsl:variable name="oddRow" select="position() mod 2" />
                                            <xsl:variable name="paymentHistory1" select="paymentHistory" />
                                            <xsl:variable name="paymentHistory2" select="paymentHistory2" />
                                            <xsl:variable name="paymentHistory1Length" select="string-length(paymentHistory)" />
                                            <xsl:variable name="paymentHistory2Length" select="paymentHistory2FieldLength" />
                                            <xsl:variable name="paymentHistoryStartMonth" select="substring(paymentStartDate,3,2)" />
                                            <xsl:variable name="paymentHistoryStartYear" select="substring(paymentStartDate,7,2)" />
                                            <!-- when payment history 1 or 2 is displaying upto 18 month then we need to do +6 or -6 -->
                                            <xsl:variable name="paymentHistory2StartMonth">
                                                <xsl:choose>
                                                    <xsl:when test="$paymentHistoryStartMonth &lt;= 6">
                                                        <xsl:value-of select="$paymentHistoryStartMonth + 6"></xsl:value-of>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:value-of select="$paymentHistoryStartMonth - 6"></xsl:value-of>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:variable>
                                            <xsl:variable name="paymentHistory2StartYear">
                                                <xsl:choose>
                                                    <xsl:when test="$paymentHistoryStartMonth &lt;= 6">
                                                        <xsl:value-of select="$paymentHistoryStartYear - 2"></xsl:value-of>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:value-of select="$paymentHistoryStartYear - 1"></xsl:value-of>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:variable>
                                            <!--<xsl:variable name="paymentHistory2Formatted" select="usr:formatDate(string(paymentStartDate))" />-->
                                            <xsl:variable name="paymentHistory2Formatted">
                                                <xsl:call-template name="formatDate">
                                                    <xsl:with-param name="inpDate" select="string(paymentStartDate)"/>
                                                </xsl:call-template>
                                            </xsl:variable>
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="250px" class="BlueLabel padAll5">ACCOUNT</td>
                                                <td width="250px" class="BlueLabel padAll5">DATES</td>
                                                <td width="250px" class="BlueLabel padAll5">AMOUNTS</td>
                                                <td width="250px" class="BlueLabel padAll5">STATUS</td>
                                            </tr>
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td colspan="4" height="8px"></td>
                                            </tr>
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td width="250px" class="BlackLabel padAll5" style="vertical-align:top">
                                                    <table>
                                                        <tr>
                                                            <td width="250px" class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">MEMBER NAME:</span>
                                                                <xsl:choose>
                                                                    <xsl:when test="memberShortName != ''">
                                                                        <xsl:value-of select="memberShortName"/>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>NOT DISCLOSED</xsl:otherwise>
                                                                </xsl:choose>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td width="250px" class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">ACCOUNT NUMBER:</span>
                                                                <xsl:choose>
                                                                    <xsl:when test="accountNumber != ''">
                                                                        <xsl:value-of select="accountNumber"/>
                                                                    </xsl:when>
                                                                    <xsl:otherwise>NOT DISCLOSED</xsl:otherwise>
                                                                </xsl:choose>
                                                            </td>
                                                        </tr>
                                                        <xsl:if test="accountType != ''">
                                                            <tr>
                                                                <td width="250px" class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">TYPE:</span>
                                                                    <!--<xsl:value-of select="usr:getAccountType(string(accountType))"/>-->
                                                                    <xsl:call-template name="getAccountType">
                                                                        <xsl:with-param name="id" select="string(accountType)"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                        <xsl:if test="ownershipIndicator != ''">
                                                            <tr>
                                                                <td width="250px" class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">OWNERSHIP:</span>
                                                                    <!--<xsl:value-of select="usr:getOwnershipInd(string(ownershipIndicator))"/>-->
                                                                    <xsl:call-template name="getOwnershipInd">
                                                                        <xsl:with-param name="ownerShipIndicator" select="string(ownershipIndicator)"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                        <xsl:if test="collateralValue != ''">
                                                            <tr>
                                                                <td width="250px" class="BlackLabel padAll5">
                                                                    <xsl:choose>
                                                                        <xsl:when test="collateralValue !=''">
                                                                            <span class="GreyItalicLabel">COLLATERAL VALUE:</span>
                                                                        </xsl:when>
                                                                        <xsl:otherwise>
                                                                            <span class="GreyItalicLabel">COLLATERAL VALUE:</span>
                                                                        </xsl:otherwise>
                                                                    </xsl:choose>
                                                                 <xsl:choose>
                                                                <xsl:when test="collateralValue !=''">
                                                                    <xsl:value-of select="collateralValue"/>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <xsl:value-of select="collateralValue"/>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="collateralType != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <xsl:choose>
                                                                <xsl:when test="collateralType !=''">
                                                                    <span class="GreyItalicLabel">COLLATERAL TYPE:</span>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <span class="GreyItalicLabel">COLLATERAL TYPE:</span>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                            <xsl:choose>
                                                                <xsl:when test="collateralType !=''">
                                                                    <!--<xsl:value-of select="usr:getCollateral(string(collateralType))"/>-->
                                                                    <xsl:call-template name="getCollateral">
                                                                        <xsl:with-param name="collId" select="string(collateralType)"/>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <!--<xsl:value-of select="usr:getCollateral(string(collateralType))"/>-->
                                                                    <xsl:call-template name="getCollateral">
                                                                        <xsl:with-param name="collId" select="string(collateralType)"/>
                                                                    </xsl:call-template>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <![CDATA[ ]]>
                                                        
                                                        
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                            </table>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5" style="vertical-align:top">
                                            <table>
                                                <xsl:if test="dateOpened != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">OPENED:</span>
                                                            <!--<xsl:value-of select="usr:formatDate(string(dateOpened))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(dateOpened)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="lastPaymentDate != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">LAST PAYMENT:</span>
                                                            <!--<xsl:value-of select="usr:formatDate(string(lastPaymentDate))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(lastPaymentDate)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="dateClosed != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">CLOSED:</span>
                                                            <!--<xsl:value-of select="usr:formatDate(string(dateClosed))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(dateClosed)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="dateReported != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <div class="GreyItalicLabel">REPORTED AND CERTIFIED:</div>
                                                            <!--<xsl:value-of select="usr:formatDate(string(dateReported))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(dateReported)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="paymentStartDate != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">PMT HIST START:</span>
                                                            <!--<xsl:value-of select="usr:formatDate(string(paymentStartDate))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(paymentStartDate)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="paymentEndDate != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">PMT HIST END:</span>
                                                            <!--<xsl:value-of select="usr:formatDate(string(paymentEndDate))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(paymentEndDate)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <tr>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <![CDATA[ ]]>
                                                    
                                                    
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5" style="vertical-align:top">
                                            <table>
                                                <xsl:if test="highCreditAmount != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <xsl:choose>
                                                                <xsl:when test="accountType ='10'
                                    or accountType ='16' or accountType ='31' 
                                    or accountType ='31' or accountType ='36' 
                                    or accountType ='37'">
                                                                    <span class="GreyItalicLabel">HIGH CREDIT:</span>
                                                                </xsl:when>
                                                                <xsl:otherwise>
                                                                    <span class="GreyItalicLabel">SANCTIONED:</span>
                                                                </xsl:otherwise>
                                                            </xsl:choose>
                                                            <xsl:choose>
                                                                <xsl:when test="highCreditAmount != ''">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/HighCreditOrSanctionedAmount, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="highCreditAmount">
																					</xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="currentBalance != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">CURRENT BALANCE:</span>
                                                            <xsl:choose>
                                                                <xsl:when test="currentBalance != '0'">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/CurrentBalance, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="currentBalance">
																					</xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise>0</xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="creditLimit != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">CREDIT LIMIT:</span>
                                                            <xsl:choose>
                                                                <xsl:when test="creditLimit != ''">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/CreditLimit, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="creditLimit"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="(string(creditLimit) = '') and (string(accountType) ='10'
                                or string(accountType) ='16' or string(accountType) ='31' 
                                or string(accountType) ='31' or string(accountType) ='36' 
                                or string(accountType) ='37')">
                                                    <tr>
                                                        <xsl:choose>
                                                            <xsl:when test="creditLimit != ''">
                                                                <td width="250px" class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">CREDIT LIMIT:</span>
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/CreditLimit, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="creditLimit"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </xsl:when>
                                                            <xsl:otherwise></xsl:otherwise>
                                                        </xsl:choose>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="cashLimit != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">CASH LIMIT:</span>
                                                            <xsl:choose>
                                                                <xsl:when test="cashLimit != ''">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/CashLimit, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="cashLimit"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="(string(cashLimit) = '') and (string(accountType) ='10'
                                or string(accountType) ='16' or string(accountType) ='31' 
                                or string(accountType) ='31' or string(accountType) ='36' 
                                or string(accountType) ='37')">
                                                    <tr>
                                                        <xsl:choose>
                                                            <xsl:when test="cashLimit != ''">
                                                                <td width="250px" class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">CASH LIMIT:</span>
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/CashLimit, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="cashLimit"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </xsl:when>
                                                            <xsl:otherwise></xsl:otherwise>
                                                        </xsl:choose>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="amountOverdue != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">OVERDUE:</span>
                                                            <xsl:choose>
                                                                <xsl:when test="amountOverdue != ''">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/AmountOverdue, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="amountOverdue"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="emiAmount != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">EMI:</span>
                                                            <xsl:choose>
                                                                <xsl:when test="emiAmount != ''">
                                                                    <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/EmiAmount, '#,###')"/>-->
                                                                    <xsl:call-template name="AmountCommaSeperator">
                                                                        <xsl:with-param name="Amount" select="emiAmount"></xsl:with-param>
                                                                    </xsl:call-template>
                                                                </xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="paymentFrequency != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">PMT FREQ:</span>
                                                            <!--<xsl:value-of select="Account_NonSummary_Segment_Fields/PaymentFrequency"/>-->
                                                            <xsl:choose>
                                                                <xsl:when test="paymentFrequency = 01">
																				Weekly
																			</xsl:when>
                                                                <xsl:when test="paymentFrequency = 02">
																				Fortnightly
																			</xsl:when>
                                                                <xsl:when test="paymentFrequency = 03">
																				Monthly
																			</xsl:when>
                                                                <xsl:when test="paymentFrequency = 04">
																				Quarterly
																			</xsl:when>
																<xsl:when test="paymentFrequency = 05">
																				Bullet payment
																				</xsl:when>
																<xsl:when test="paymentFrequency = 06">
																				Daily
																				</xsl:when>
																<xsl:when test="paymentFrequency = 07">
																				Half yearly
																				</xsl:when>
																<xsl:when test="paymentFrequency = 08">
																				Yearly
																				</xsl:when>
																<xsl:when test="paymentFrequency = 09">
																				On-demand
																				</xsl:when>
                                                                <xsl:otherwise></xsl:otherwise>
                                                            </xsl:choose>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="paymentTenure != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">REPAYMENT TENURE:</span>
                                                            <xsl:value-of select="paymentTenure"/>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="interestRate != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">INTEREST RATE:</span>
                                                            <xsl:value-of select="interestRate"/>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="actualPaymentAmount != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">ACTUAL PAYMENT:</span>
                                                            <!--<xsl:value-of select="Account_NonSummary_Segment_Fields/ActualPaymentAmount"/>-->
                                                            <xsl:call-template name="AmountCommaSeperator">
                                                                <xsl:with-param name="Amount" select="actualPaymentAmount"></xsl:with-param>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <tr>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <![CDATA[ ]]>
                                                    
                                                    
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5" style="vertical-align:top">
                                            <table>
                                                <xsl:if test="(suitFiled != '') and (suitFiled != '00')">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">SUIT FILED /WILFUL DEFAULT:</span>
                                                            <!--<xsl:value-of select="usr:getSuitFileorWilfulDefault(string(suitFiled))"/>-->
                                                            <xsl:call-template name="getSuitFileorWilfulDefault">
                                                                <xsl:with-param name="suiteId" select="string(suitFiled)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="(WrittenOffAndSettled != '') and (WrittenOffAndSettled != '00')">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <div class="GreyItalicLabel">CREDIT FACILITY STATUS:</div>
                                                            <!--<xsl:value-of select="usr:getWrittenOffSettledStatus(string(WrittenOffAndSettled))"/>-->
                                                            <xsl:call-template name="getWrittenOffSettledStatus">
                                                                <xsl:with-param name="woStId" select="string(WrittenOffAndSettled)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="(creditFacilityStatus != '') and (creditFacilityStatus != '00')">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <div class="GreyItalicLabel">CREDIT FACILITY STATUS:</div>
                                                            <!--<xsl:value-of select="usr:getWrittenOffSettledStatus(string(creditFacilityStatus))"/>-->
                                                            <xsl:call-template name="getWrittenOffSettledStatus">
                                                                <xsl:with-param name="woStId" select="string(creditFacilityStatus)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="woAmountTotal != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">WRITTEN OFF (TOTAL):</span>
                                                            <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/WrittenOffAmountTotal, '#,###')"/>-->
                                                            <xsl:call-template name="AmountCommaSeperator">
                                                                <xsl:with-param name="Amount" select="woAmountTotal"></xsl:with-param>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="woAmountPrincipal != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">WRITTEN OFF (PRINCIPAL):</span>
                                                            <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/WrittenOffAmountPrincipal, '#,###')"/>-->
                                                            <xsl:call-template name="AmountCommaSeperator">
                                                                <xsl:with-param name="Amount" select="woAmountPrincipal"></xsl:with-param>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <xsl:if test="settlementAmount != ''">
                                                    <tr>
                                                        <td width="250px" class="BlackLabel padAll5">
                                                            <span class="GreyItalicLabel">SETTLEMENT:</span>
                                                            <!--<xsl:value-of select="format-number(Account_NonSummary_Segment_Fields/SettlementAmount, '#,###')"/>-->
                                                            <xsl:call-template name="AmountCommaSeperator">
                                                                <xsl:with-param name="Amount" select="settlementAmount"></xsl:with-param>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </xsl:if>
                                                <tr>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <![CDATA[ ]]>
                                                    
                                                    
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="750px" colspan="3" class="BlueLabel padAll5">DAYS PAST DUE/ASSET CLASSIFICATION (UP TO 36 MONTHS; LEFT TO RIGHT)</td>
                                        <td width="250px" class="BlueLabel padAll5"></td>
                                    </tr>
                                    <tr>
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td colspan="4" height="8px"></td>
                                    </tr>
                                    <tr>
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="1000px" colspan="4" class="BlackLabel padAll5">
                                            <xsl:call-template name="generatePaymentHistory">
                                                <xsl:with-param name="phLength" select="$paymentHistory1Length"/>
                                                <xsl:with-param name="phString" select="$paymentHistory1"/>
                                                <xsl:with-param name="phStartLength">1</xsl:with-param>
                                                <xsl:with-param name="phStartMonth">
                                                    <xsl:value-of select="$paymentHistoryStartMonth"/>
                                                </xsl:with-param>
                                                <xsl:with-param name="phStartYear">
                                                    <xsl:value-of select="$paymentHistoryStartYear"/>
                                                </xsl:with-param>
                                            </xsl:call-template>
                                        </td>
                                        <tr>
                                            <xsl:if test="$oddRow">
                                                <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                            </xsl:if>
                                            <td width="1000px" colspan="4" class="BlackLabel padAll5">
                                                <xsl:call-template name="generatePaymentHistory">
                                                    <xsl:with-param name="phLength" select="$paymentHistory2Length"/>
                                                    <xsl:with-param name="phString" select="$paymentHistory2"/>
                                                    <xsl:with-param name="phStartLength">1</xsl:with-param>
                                                    <xsl:with-param name="phStartMonth">
                                                        <xsl:value-of select=" $paymentHistory2StartMonth"/>
                                                    </xsl:with-param>
                                                    <xsl:with-param name="phStartYear">
                                                        <xsl:value-of select="$paymentHistory2StartYear"/>
                                                    </xsl:with-param>
                                                </xsl:call-template>
                                            </td>
                                        </tr>
                                        <xsl:if test="(ErrorCode != '') or (cibilRemarksCode != '')">
                                            <tr>
                                                <xsl:if test="$oddRow">
                                                    <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                </xsl:if>
                                                <td  width="1000px" class="greyallborder15" colspan="4">
                                                    <table>
                                                        <tr>
                                                            <td class="BlackLabel padAll5">
                                                                <span class="GreyItalicLabel">INFORMATION UNDER DISPUTE:</span>
                                                                <!--<xsl:value-of select="usr:ToUpper(usr:getAccountDisputeDesc(string(ErrorCode)))"/>-->
                                                                <xsl:variable name="disputeDesc">
                                                                    <xsl:call-template name="getAccountDisputeDesc">
                                                                        <xsl:with-param name="disputeId" select="string(ErrorCode)"/>
                                                                    </xsl:call-template>
                                                                </xsl:variable>
                                                                <xsl:call-template name="ToUpper">
                                                                    <xsl:with-param name="data" select="$disputeDesc"/>
                                                                </xsl:call-template>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <xsl:if test="$oddRow">
                                                                <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                            </xsl:if>
                                                            <td colspan="4" height="8px"></td>
                                                        </tr>
                                                        <xsl:if test="ErrorDisputeRemarksCode1 != ''">
                                                            <tr>
                                                                <td class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">DISPUTE REMARKS:</span>
                                                                    <!--<xsl:value-of select="usr:ToUpper(usr:getDisputeRemarkCodeDesc(string(ErrorDisputeRemarksCode1)))"/>-->
                                                                    <xsl:variable name="dispRmCodeDesc1">
                                                                        <xsl:call-template name="getDisputeRemarkCodeDesc">
                                                                            <xsl:with-param name="id" select="string(ErrorDisputeRemarksCode1)"/>
                                                                        </xsl:call-template>
                                                                    </xsl:variable>
                                                                    <xsl:call-template name="ToUpper">
                                                                        <xsl:with-param name="data" select="$dispRmCodeDesc1"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                        <xsl:if test="ErrorDisputeRemarksCode2 != ''">
                                                            <tr>
                                                                <td class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">DISPUTE REMARKS #2:</span>
                                                                    <!--<xsl:value-of select="usr:ToUpper(usr:getDisputeRemarkCodeDesc(string(ErrorDisputeRemarksCode2)))"/>-->
                                                                    <xsl:variable name="dispRmCodeDesc2">
                                                                        <xsl:call-template name="getDisputeRemarkCodeDesc">
                                                                            <xsl:with-param name="id" select="string(ErrorDisputeRemarksCode2)"/>
                                                                        </xsl:call-template>
                                                                    </xsl:variable>
                                                                    <xsl:call-template name="ToUpper">
                                                                        <xsl:with-param name="data" select="$dispRmCodeDesc2"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                        <xsl:if test="cibilRemarksCode != ''">
                                                            <tr>
                                                                <td class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">CIBIL REMARKS:</span>
                                                                    <!--<xsl:value-of select="usr:ToUpper(usr:getRemarkCodeDesc(string(cibilRemarksCode)))"/>-->
                                                                    <xsl:variable name="remarkCodeDesc">
                                                                        <xsl:call-template name="getRemarkCodeDesc">
                                                                            <xsl:with-param name="id" select="string(cibilRemarksCode)"/>
                                                                        </xsl:call-template>
                                                                    </xsl:variable>
                                                                    <xsl:call-template name="ToUpper">
                                                                        <xsl:with-param name="data" select="$remarkCodeDesc"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                        <xsl:if test="DateOfEntryForcibilRemarksCode != ''">
                                                            <tr>
                                                                <td class="BlackLabel padAll5">
                                                                    <span class="GreyItalicLabel">DATE ENTERED:</span>
                                                                    <!--<xsl:value-of select="usr:formatDate(string(DateOfEntryForcibilRemarksCode))"/>-->
                                                                    <xsl:call-template name="formatDate">
                                                                        <xsl:with-param name="inpDate" select="string(DateOfEntryForcibilRemarksCode)"/>
                                                                    </xsl:call-template>
                                                                </td>
                                                            </tr>
                                                        </xsl:if>
                                                    </table>
                                                </td>
                                            </tr>
                                        </xsl:if>
                                    </tr>
                                </xsl:for-each>
                            </xsl:if>
                        </table>
                    </td>
                </tr>
                <!-- Account segment end-->
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <!-- Enquiry Segment Starts -->
                <tr>
                    <td>
                        <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                            <tr>
                                <td width="330px" class="constitleGreyBig">ENQUIRIES:</td>
                                <td width="300px"></td>
                                <td width="370px"></td>
                            </tr>
                            <xsl:if test="Root/root/consumerCreditData/item/enquiries != ''">
                                <tr>
                                    <td width="250px" class="BlueLabel padAll5">MEMBER</td>
                                    <td width="250px" class="BlueLabel padAll5">ENQUIRY DATE</td>
                                    <td width="250px" class="BlueLabel padAll5">ENQUIRY PURPOSE</td>
                                    <td width="250px" class="BlueLabel padAll5">ENQUIRY AMOUNT</td>
                                </tr>
                                <!-- <xsl:for-each select="Root/root/consumerCreditData/item/item/enquiries/item"> -->
                                <xsl:for-each select="//Root/root/consumerCreditData/item/enquiries/item">
                                    <xsl:variable name="oddRow" select="position() mod 2" />
                                    <tr>
                                        <xsl:if test="$oddRow">
                                            <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                        </xsl:if>
                                        <td width="250px" class="BlackLabel padAll5">
                                            <xsl:value-of select="memberShortName"/>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5">
                                            <!--<xsl:value-of select="usr:formatDate(string(enquiryDate))"/>-->
                                            <xsl:call-template name="formatDate">
                                                <xsl:with-param name="inpDate" select="string(enquiryDate)"/>
                                            </xsl:call-template>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5">
                                            <!--<xsl:value-of select="usr:getAccountType(string(enquiryPurpose))"/>-->
                                            <xsl:call-template name="getAccountType">
                                                <xsl:with-param name="id" select="string(enquiryPurpose)"/>
                                            </xsl:call-template>
                                        </td>
                                        <td width="250px" class="BlackLabel padAll5">
                                            <xsl:choose>
                                                <xsl:when test="enquiryAmount != ''">
                                                    <!--<xsl:value-of select="format-number(EnquiryAmount, '#,###')"/>-->
                                                    <xsl:call-template name="AmountCommaSeperator">
                                                        <xsl:with-param name="Amount" select="enquiryAmount"></xsl:with-param>
                                                    </xsl:call-template>
                                                </xsl:when>
                                                <xsl:otherwise></xsl:otherwise>
                                            </xsl:choose>
                                        </td>
                                    </tr>
                                </xsl:for-each>
                            </xsl:if>
                        </table>
                    </td>
                </tr>
                <!-- Enquiry Segment Ends -->
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <!-- End of report tag starts-->
                <tr>
                    <td>
                        <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                            <tr>
                                <td colspan="4" class="BlueLabelBigger1 padAll5">
												END OF REPORT ON 
                                    
                                    
                                    <xsl:value-of select="Root/root/consumerCreditData/item/names/item/name"/>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <!-- End of report tag ends-->
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <tr>
                    <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                </tr>
                <!-- statuatory information start-->
                <tr>
                    <td align="left" colspan="2" class="padWhole">
                        <table  cellpadding="0" cellspacing="0"  width="100%">
                            <tr>
                                <td class="endStatement AddPad " style="font-size:11px;">
                                    <p>
                                        <strong>
														All information ("Information") contained in this credit information report (CIR) is the current and up to date information collated by TransUnion CIBIL
														Limited based on information provided by its various members ("Members"). By accessing and using the Information, the user acknowledges and accepts
														the following: While TransUnion CIBIL takes reasonable care in preparing the CIR, TransUnion CIBIL shall not be responsible for errors and/or omissions
														caused by inaccurate or inadequate information submitted to it. However, TransUnion CIBIL shall take reasonable steps to ensure accurate reproduction
														of the information submitted by the Members and, to the extent statutorily permitted, it shall correct any such inaccuracies in the CIR. Further, TransUnion
														CIBIL does not guarantee the adequacy or completeness of the information and/or its suitability for any specific purpose nor is TransUnion CIBIL
														responsible for any access or reliance on the CIR. The CIR is not a recommendation by TransUnion CIBIL to any Member to (i) lend or not to lend; (ii)
														enter into or not to enter into any financial transaction with the concerned individual/entity. Credit Scores do not form part of the CIR. The use of the CIR is
														governed by the provisions of the Credit Information Companies (Regulation) Act, 2005, the Credit Information Companies Regulations, 2006, Credit
														Information Companies Rules, 2006 and the terms and conditions of the Operating Rules for TransUnion CIBIL and its Members.
													</strong>
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr style="margin-top:4px;">
                    <td align="left" colspan="2" class="padWhole" style="padding-top:11px; padding-bottom:7px;" valign="top">
                        <table cellpadding="0" cellspacing="0" width="100%" style="border-top: 1.5px solid #00a6c9;">
                            <tr>
                                <td width="100%" align="center"  style="font-size:11px;font-weight: bolder">© 2023 TransUnion CIBIL Limited. (Formerly: Credit Information Bureau (India) Limited). All rights reserved</td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td width="100%" align="center"  style="font-size:11px;font-weight: bolder">TransUnion CIBIL CIN : U72300MH2000PLC128359</td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <!-- statuatory information end-->
				
				
                <!---Secondary Match Start -->
                <xsl:if test="Root/root/consumerCreditData != ''">
                    <tr>
                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                    </tr>
                    <tr>
                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                    </tr>
                    <tr>
                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                    </tr>
                    <tr>
                        <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                    </tr>
                    <xsl:for-each select="Root/root/consumerCreditData">
                        <xsl:variable name="show_Multilist" select="position()" />
                        <xsl:if test="$show_Multilist != 1">
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greyborder25" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="650px" class="constitleRedBig">
														ADDITIONAL MATCHES -- YOUR ENQUIRY ON 
                                                
                                                
                                                <xsl:value-of select="string($ConsumerName)"/> RETURNED MULTIPLE FILES. SEE INFORMATION
														RELATED TO ADDITIONAL SUBJECT
                                                <xsl:value-of select="concat(Root/root/consumerCreditData/item/NameSegment/ConsumerName1, ' ' ,Root/root/consumerCreditData/item/NameSegment/ConsumerName2,
                        ' ' ,Root/root/consumerCreditData/item/NameSegment/ConsumerName3, ' ' ,Root/root/consumerCreditData/item/NameSegment/ConsumerName4, ' ' ,Root/root/consumerCreditData/item/NameSegment/ConsumerName5)"/> BELOW.
                                            </td>
                                            <td width="400px"></td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Consumer Information Start -->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greyborder" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">CONSUMER INFORMATION:</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <tr>
                                            <td width="600px">
                                                <table>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">NAME:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <!-- in CIR MR is there. check Mr. Ms to add -->
                                                            <xsl:value-of select="names/name"/>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">DATE OF BIRTH:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <!--<xsl:value-of select="usr:formatDate(string(names/item/birthDate))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(names/birthDate)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td width="300px">
                                                <table>
                                                    <tr>
                                                        <td height="14px"  bgcolor="#FFFFFF"></td>
                                                    </tr>
                                                    <tr>
                                                        <td class="GreyItalicLabel"  align="left" colspan="2">GENDER:</td>
                                                        <td class="BlackLabel"  align="left" colspan="2">
                                                            <!--<xsl:value-of select="usr:Getgender(string(names/item/gender))"/>-->
                                                            <xsl:call-template name="Getgender">
                                                                <xsl:with-param name="gender" select="string(names/gender)"/>
                                                            </xsl:call-template>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Consumer Information End -->
                            <tr>
                                <td colspan="4" height="8px"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px"></td>
                            </tr>
                            <!-- Identifiation segment starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">IDENTIFICATION(S):</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <xsl:if test="ids !=''">
                                            <tr>
                                                <td width="250px" class="BlueLabel">IDENTIFICATION TYPE</td>
                                                <td width="250px" class="BlueLabel">IDENTIFICATION NUMBER</td>
                                                <td width="250px" class="BlueLabel">ISSUE DATE</td>
                                                <td width="250px" class="BlueLabel">EXPIRATION DATE</td>
                                            </tr>
                                            <xsl:for-each select="ids">
                                                <xsl:variable name="oddRow" select="position() mod 2" />
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="idType = '01'">
																		INCOME TAX ID NUMBER (PAN)
																	</xsl:when>
                                                            <xsl:when test="idType = '02'">
																		PASSPORT NUMBER
																	</xsl:when>
                                                            <xsl:when test="idType = '03'">
																		VOTER ID
																	</xsl:when>
                                                            <xsl:when test="idType = '04'">
																		DRIVER'S LICENSE NUMBER
																	</xsl:when>
                                                            <xsl:when test="idType = '05'">
																		RATION CARD NUMBER
																	</xsl:when>
                                                            <xsl:when test="idType = '06'">
																		AADHAAR NUMBER
																	</xsl:when>
															<xsl:when test="idType = '09'">
																CKYC
																	</xsl:when>
															<xsl:when test="idType = '10'">
																NREGA CARD NUMBER
																</xsl:when>
                                                            <xsl:otherwise>
																		NOT CLASSIFIED
																	</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <xsl:value-of select="idNumber"/>
                                                    </td>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <!--<xsl:value-of select="usr:formatDate(string(IssueDate))"/>-->
                                                        <xsl:call-template name="formatDate">
                                                            <xsl:with-param name="inpDate" select="string(IssueDate)"/>
                                                        </xsl:call-template>
                                                    </td>
                                                    <td width="250px" class="BlackLabel padAll5">
                                                        <!--<xsl:value-of select="usr:formatDate(string(ExpirationDate))"/>-->
                                                        <xsl:call-template name="formatDate">
                                                            <xsl:with-param name="inpDate" select="string(ExpirationDate)"/>
                                                        </xsl:call-template>
                                                    </td>
                                                </tr>
                                            </xsl:for-each>
                                        </xsl:if>
                                    </table>
                                </td>
                            </tr>
                            <!-- identification segment end-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- telephone segment starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">TELEPHONE(S):</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <xsl:if test="telephones !=''">
                                            <tr>
                                                <td width="300px" class="BlueLabel">TELEPHONE TYPE</td>
                                                <td width="330px" class="BlueLabel">TELEPHONE NUMBER</td>
                                                <td width="370px" class="BlueLabel">TELEPHONE EXTENSION</td>
                                            </tr>
                                            <xsl:for-each select="telephones">
                                                <xsl:variable name="oddRow" select="position() mod 2" />
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="300px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="telephoneType = '01'">
																		MOBILE PHONE
																		
                                                                
                                                                
                                                                <xsl:if test="enquiryEnriched = 'Y'">
                                                                    <sup>(e)</sup>
                                                                </xsl:if>
                                                            </xsl:when>
                                                            <xsl:when test="telephoneType = '02'">
																		HOME PHONE
																		
                                                                
                                                                
                                                                <xsl:if test="enquiryEnriched = 'Y'">
                                                                    <sup>(e)</sup>
                                                                </xsl:if>
                                                            </xsl:when>
                                                            <xsl:when test="telephoneType = '03'">
																		OFFICE PHONE
																		
                                                                
                                                                
                                                                <xsl:if test="enquiryEnriched = 'Y'">
                                                                    <sup>(e)</sup>
                                                                </xsl:if>
                                                            </xsl:when>
                                                            <xsl:otherwise>
																		NOT CLASSIFIED
																		
                                                                
                                                                
                                                                <xsl:if test="enquiryEnriched = 'Y'">
                                                                    <sup>(e)</sup>
                                                                </xsl:if>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="330px" class="BlackLabel padAll5">
                                                        <xsl:value-of select="telephoneNumber"/>
                                                    </td>
                                                    <td width="370px" class="BlackLabel padAll5">
                                                        <xsl:value-of select="TelephoneExtension"/>
                                                    </td>
                                                </tr>
                                            </xsl:for-each>
                                        </xsl:if>
                                    </table>
                                </td>
                            </tr>
                            <!-- telephone segment end-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- email segment starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">EMAIL CONTACT(S):</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <xsl:if test="emails != ''">
                                            <tr>
                                                <td width="300px" class="BlueLabel">EMAIL ADDRESS</td>
                                                <td width="330px" class="BlueLabel"></td>
                                                <td width="370px" class="BlueLabel"></td>
                                            </tr>
                                            <xsl:for-each select="emails">
                                                <xsl:variable name="oddRow" select="position() mod 2" />
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="300px" class="BlackLabel padAll5">
                                                        <xsl:value-of select="emailID"/>
                                                    </td>
                                                    <td width="330px" class="BlackLabel padAll5">
															</td>
                                                    <td width="370px" class="BlackLabel padAll5"></td>
                                                </tr>
                                            </xsl:for-each>
                                        </xsl:if>
                                    </table>
                                </td>
                            </tr>
                            <!-- email segment end-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- address segment starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="300px" class="constitleGreyBig">ADDRESS(ES):</td>
                                            <td width="330px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <xsl:if test="addresses != ''">
                                            <xsl:for-each select="addresses">
                                                <xsl:variable name="oddRow" select="position() mod 2" />
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="975px" colspan="3" class="BlueLabel padAll5">
																ADDRESS:
                                                        
                                                        
                                                        <span class="BlackLabel">
                                                            <xsl:if test="line1 != ''">
                                                                <xsl:value-of select="line1"/>
                                                            </xsl:if>
                                                            <xsl:if test="line2 != ''">
																		,
                                                                
                                                                
                                                                <xsl:value-of select="line2"/>
                                                            </xsl:if>
                                                            <xsl:if test="line3 != ''">
																		,
                                                                
                                                                
                                                                <xsl:value-of select="line3"/>
                                                            </xsl:if>
                                                            <xsl:if test="index != ''">
																		,
                                                                
                                                                
                                                                <xsl:value-of select="index"/>
                                                            </xsl:if>
                                                            <xsl:if test="line5 != ''">
																		,
                                                                
                                                                
                                                                <xsl:value-of select="line5"/>
                                                            </xsl:if>
                                                            <xsl:if test="stateCode != ''">
																		,
                                                                
                                                                
                                                                <!--<xsl:value-of select="usr:GetState(string(stateCode))"/>-->
                                                                <xsl:call-template name="GetState">
                                                                    <xsl:with-param name="stCode" select="string(stateCode)"/>
                                                                </xsl:call-template>
                                                            </xsl:if>
                                                            <xsl:if test="pinCode != ''">
																		,
                                                                
                                                                
                                                                <xsl:value-of select="pinCode"/>
                                                            </xsl:if>
                                                        </span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="300px" class="BlackLabel padAll5">
                                                        <span class="BlueLabel">CATEGORY:</span>
                                                        <xsl:if test="addressCategory = '01'">
																	Permanent Address
																</xsl:if>
                                                        <xsl:if test="addressCategory = '02'">
																	Residence Address
																</xsl:if>
                                                        <xsl:if test="addressCategory = '03'">
																	Office Address
																</xsl:if>
                                                        <xsl:if test="addressCategory = '04'">
																	Not Categorized
																</xsl:if>
														<xsl:if test="addressCategory = '05'">
														Mortgage Property address
														</xsl:if>
                                                    </td>
                                                    <td width="330px" class="BlackLabel padAll5">
                                                        <span class="BlueLabel">RESIDENCE CODE:</span>
                                                        <xsl:choose>
                                                            <xsl:when test="residenceCode = '01'">
																		Owned
																	</xsl:when>
                                                            <xsl:when test="residenceCode = '02'">
																		Rented
																	</xsl:when>
                                                            <xsl:otherwise>

																	</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="370px">
                                                        <span class="BlueLabel">DATE REPORTED:</span>
                                                        <span class="BlackLabel">
                                                            <!--<xsl:value-of select="usr:formatDate(string(dateReported))"/>-->
                                                            <xsl:call-template name="formatDate">
                                                                <xsl:with-param name="inpDate" select="string(dateReported)"/>
                                                            </xsl:call-template>
                                                        </span>
                                                    </td>
                                                </tr>
                                            </xsl:for-each>
                                        </xsl:if>
                                    </table>
                                </td>
                            </tr>
                            <!-- address segment end-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- employment segment starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="330px" class="constitleGreyBig">EMPLOYMENT INFORMATION :</td>
                                            <td width="300px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <xsl:if test="employment != ''">
                                            <tr>
                                                <td width="165px" class="BlueLabel">ACCOUNT TYPE</td>
                                                <td width="165px" class="BlueLabel">DATE REPORTED</td>
                                                <td width="165px" class="BlueLabel">OCCUPATION CODE</td>
                                                <td width="165px" class="BlueLabel">INCOME</td>
                                                <td width="165px" class="BlueLabel">NET / GROSS INCOME INDICATOR</td>
                                                <td width="175px" class="BlueLabel">MONTHLY / ANNUAL INCOME INDICATOR</td>
                                            </tr>
                                            <xsl:for-each select="employment">
                                                <xsl:variable name="oddRow" select="position() mod 2" />
                                                <tr>
                                                    <xsl:if test="$oddRow">
                                                        <xsl:attribute name="class">alternatetdbggrey</xsl:attribute>
                                                    </xsl:if>
                                                    <td width="165px" class="BlackLabel padAll5">
                                                        <!-- TODO: Complete script to match the account type value -->
                                                        <!--<xsl:value-of select="usr:getAccountType(string(accountType))"/>-->
                                                        <xsl:call-template name="getAccountType">
                                                            <xsl:with-param name="id" select="string(accountType)"/>
                                                        </xsl:call-template>
                                                    </td>
                                                    <td width="165px" class="BlackLabel padAll5">
                                                        <!-- TODO: Complete script to form date properly in dd-mm-yyyy -->
                                                        <!--<xsl:value-of select="usr:formatDate(string(dateReported))"/>-->
                                                        <xsl:call-template name="formatDate">
                                                            <xsl:with-param name="inpDate" select="string(dateReported)"/>
                                                        </xsl:call-template>
                                                    </td>
                                                    <td width="165px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="occupationCode = '01'">
																		Salaried
																	</xsl:when>
                                                            <xsl:when test="occupationCode = '02'">
																		Self Employed Professional
																	</xsl:when>
                                                            <xsl:when test="occupationCode = '03'">
																		Self Employed
																	</xsl:when>
                                                            <xsl:when test="occupationCode = '04'">
																		Others
																	</xsl:when>
                                                            <xsl:otherwise>

																	</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="165px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="Income != ''">
                                                                <!--<xsl:value-of select="format-number(Income, '#,###')"/>-->
                                                                <xsl:call-template name="AmountCommaSeperator">
                                                                    <xsl:with-param name="Amount" select="Income"></xsl:with-param>
                                                                </xsl:call-template>
                                                            </xsl:when>
                                                            <xsl:otherwise>Not Available</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="165px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="NetGrossIndicator = 'G'">
																		Gross Income
																	</xsl:when>
                                                            <xsl:when test="NetGrossIndicator = 'N'">
																		Net Income
																	</xsl:when>
                                                            <xsl:otherwise>Not Available</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                    <td width="175px" class="BlackLabel padAll5">
                                                        <xsl:choose>
                                                            <xsl:when test="MonthlyAnnualIndicator = 'M'">
																		Monthly
																	</xsl:when>
                                                            <xsl:when test="MonthlyAnnualIndicator = 'A'">
																		Annual
																	</xsl:when>
                                                            <xsl:otherwise>Not Available</xsl:otherwise>
                                                        </xsl:choose>
                                                    </td>
                                                </tr>
                                            </xsl:for-each>
                                        </xsl:if>
                                    </table>
                                </td>
                            </tr>
                            <!-- employment segment end-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- end of report starts-->
                            <tr>
                                <td>
                                    <table width="1000" border="0" align="right" class="greybordernopadding" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td width="330px" class="BlueLabelBigger1 padAll5">
														END OF REPORT ON 
                                                
                                                
                                                <xsl:value-of select="names/name"/>
                                            </td>
                                            <td width="300px"></td>
                                            <td width="370px"></td>
                                        </tr>
                                        <tr>
                                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                        </tr>
                                        <tr>
                                            <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- end of report ends-->
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <tr>
                                <td colspan="4" height="8px" bgcolor="#FFFFFF"></td>
                            </tr>
                            <!-- Success End-->
								
								
                        
                        
                        </xsl:if>
                    </xsl:for-each>
                    <xsl:variable name="NoConsumerVarCount" select="count(Root/root/consumerCreditData)" />
                    <xsl:if test="$NoConsumerVarCount > 1">
                        <tr>
                            <td align="left" colspan="2" class="padWhole">
                                <table  cellpadding="0" cellspacing="0"  width="100%">
                                    <tr>
                                        <td class="endStatement AddPad " style="border:1px solid #00a6ca;font-size:11px;">
                                            <p>
                                                <strong>
														All information contained in this credit report has been collated by TransUnion CIBIL Limited (TU CIBIL) based on information provided / submitted by 
														its various members ("Members"), as part of periodic data submission and Members are required to ensure accuracy, completeness and veracity of the 
														information submitted. The credit report is generated using the proprietary search and match logic of TU CIBIL. TU CIBIL uses its best efforts to 
														ensure accuracy, completeness and veracity of the information contained in the Report, and shall only be liable and / or responsible if any 
														discrepancies are directly attributable to TU CIBIL. The use of this report is governed by the terms and conditions of the Operating Rules for TU CIBIL 
														and its Members.

														</strong>
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr style="margin-top:4px;">
                            <td align="left" colspan="2" class="padWhole" style="padding-top:11px; padding-bottom:7px;" valign="top">
                                <table cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td width="100%" align="center"  style="border:1px solid #00a6ca;font-size:11px;font-weight: bolder">© 2023 TransUnion CIBIL Limited. (Formerly: Credit Information Bureau (India) Limited). All rights reserved</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </xsl:if>
                </xsl:if>
                <!---Secondary Match End -->


            </table>
        </xsl:otherwise>
    </xsl:choose>
</body>
</html>
</xsl:template>



<xsl:template name="generatePaymentHistory">
    <xsl:param name="phLength"/>
    <xsl:param name="phString"/>
    <xsl:param name="phStartLength"/>
    <xsl:param name="phStartMonth"/>
    <xsl:param name="phStartYear" />
    <xsl:if test="$phLength > 0">
        <xsl:if test="$phStartLength &lt;= $phLength">
            <div class="PhDiv50Width">
                <xsl:value-of select="substring($phString,$phStartLength,3)"></xsl:value-of>
                <br/>
                <xsl:choose>
                    <xsl:when test="string-length($phStartMonth) = 2 and string-length($phStartYear) = 1">
                        <xsl:value-of select="$phStartMonth"></xsl:value-of>-0
                        <xsl:value-of select="$phStartYear"></xsl:value-of>
                    </xsl:when>
                    <xsl:when test="string-length($phStartMonth) = 1 and string-length($phStartYear) = 1">
							0
                        
                        
                        <xsl:value-of select="$phStartMonth"></xsl:value-of>-0
                        <xsl:value-of select="$phStartYear"></xsl:value-of>
                    </xsl:when>
                    <xsl:when test="string-length($phStartMonth) = 1">
							0
                        
                        
                        <xsl:value-of select="$phStartMonth"></xsl:value-of>-
                        <xsl:value-of select="$phStartYear"></xsl:value-of>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$phStartMonth"></xsl:value-of>-
                        <xsl:value-of select="$phStartYear"></xsl:value-of>
                    </xsl:otherwise>
                </xsl:choose>
            </div>
            <xsl:call-template name="generatePaymentHistory">
                <xsl:with-param name="phLength" select="$phLength"/>
                <xsl:with-param name="phString" select="$phString"/>
                <xsl:with-param name="phStartLength" select="$phStartLength + 3"/>
                <xsl:with-param name="phStartMonth">
                    <xsl:if test="$phStartMonth = 1">12</xsl:if>
                    <xsl:if test="$phStartMonth != 1">
                        <xsl:value-of select="$phStartMonth - 1"></xsl:value-of>
                    </xsl:if>
                </xsl:with-param>
                <xsl:with-param name="phStartYear">
                    <xsl:if test="$phStartMonth = 1">
                        <xsl:value-of select="$phStartYear - 1"></xsl:value-of>
                    </xsl:if>
                    <xsl:if test="$phStartMonth != 1">
                        <xsl:value-of select="$phStartYear"></xsl:value-of>
                    </xsl:if>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:if>
    </xsl:if>
</xsl:template>
<xsl:template name="AmountCommaSeperator">
    <xsl:param name="Amount" />
    <xsl:choose>
        <xsl:when test="$Amount >= 1000">
            <xsl:value-of select="format-number(floor($Amount div 1000), '#,##')" />
            <xsl:text>,</xsl:text>
            <xsl:value-of select="format-number($Amount mod 1000, '000')" />
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="format-number($Amount, '0')" />
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<xsl:strip-space elements="*"/>
<xsl:strip-space elements="*"/>


<!--Main Template for getting scoring factor -->
<xsl:template name="generateScoringFactors">
    <xsl:param name="counter"/>
    <xsl:param name="ForScore"/>
<!-- Template for getting Exlusion Code  -->	
    <xsl:variable name="nodecounter" select="concat('exclusionCode',$counter)"></xsl:variable>
    <xsl:for-each select="//Root/root/consumerCreditData/item/scores/item[$counter]">
        <xsl:if test ="scoreCardName = $ForScore">
            <xsl:for-each select="exclusionCodes">
                <xsl:variable name="nodecountervalue" select="exclusionCodeValue"></xsl:variable>
                <xsl:choose>
                    <xsl:when test="string-length($nodecountervalue) > 0">
                        <xsl:variable name="exclusionReason">
                            <xsl:call-template name="getExclusionReason">
                                <xsl:with-param name="counter" select="$counter"/>
                                <xsl:with-param name="id" select="string($nodecountervalue)"/>
                            </xsl:call-template>
                        </xsl:variable>
                        <xsl:if test="$exclusionReason != ''">
                            <li class="padAll2">
                                <xsl:value-of select="$exclusionReason"/>
                            </li>
                        </xsl:if>
                </xsl:when>
                <xsl:otherwise></xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:if>
</xsl:for-each>
<!-- Template for getting Reason Code -->
<xsl:variable name="nodereasoncode" select="concat('ReasonCode',$counter)"></xsl:variable>
<xsl:for-each select="//Root/root/consumerCreditData/item/scores/item[$counter]">
        <xsl:for-each select="reasonCodes/item">
            <xsl:variable name="nodereasoncodecounter" select="reasonCodeValue"></xsl:variable>
			<xsl:choose>
	                <xsl:when test="string-length($nodereasoncodecounter) > 0">
                    <xsl:variable name="reasonCodeDescr">
                        <xsl:call-template name="getReasonCodeDescription">
                            <xsl:with-param name="id" select="string($nodereasoncodecounter)"/>
                            <xsl:with-param name="scoretype" select="string(//scoreCardName)"/>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:if test="$reasonCodeDescr !=''">
                        <li class="padAll2">
                            <xsl:value-of select="$reasonCodeDescr"/>
                        </li>
                    </xsl:if>
                </xsl:when>
                <xsl:otherwise></xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
</xsl:for-each>
<!-- Template for getting reason code End-->

<xsl:if test="$counter &lt;= 10">
    <xsl:call-template name="generateScoringFactors">
        <xsl:with-param name="counter" select="$counter + 1"/>
        <xsl:with-param name="ForScore" select="$ForScore"/>
    </xsl:call-template>
</xsl:if>
</xsl:template>
<!-- Main template end -->



<!--<xsl:template name="getEnqPast30Days"><xsl:param name="currentDate"/><xsl:param name="enqPast30Days"/><xsl:param name="noOfEnquiries"/><xsl:variable name="dateofEnquiry" select="string((Root/root/consumerCreditData/item/item/enquiries/item)[$noOfEnquiries]/enquiryDate)"></xsl:variable><xsl:variable name="daysDifference" select="usr:getDaysDifference($currentDate,usr:formatDate(string($dateofEnquiry)))"></xsl:variable><xsl:choose><xsl:when test="string($noOfEnquiries) = '0'"><xsl:value-of select="$enqPast30Days"/>
			</xsl:when><xsl:otherwise>
			</xsl:otherwise></xsl:choose><xsl:if test="$noOfEnquiries >= 0"><xsl:call-template name="getEnqPast30Days"><xsl:with-param name="currentDate" select="$currentDate"/><xsl:with-param name="enqPast30Days"><xsl:if test="$daysDifference &lt;= 30"><xsl:value-of select="$enqPast30Days + 1"></xsl:value-of></xsl:if><xsl:if test="$daysDifference > 30"><xsl:value-of select="$enqPast30Days"></xsl:value-of></xsl:if>
				</xsl:with-param><xsl:with-param name="noOfEnquiries" select="$noOfEnquiries - 1"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template><xsl:template name="getEnqPast12Months"><xsl:param name="currentDate"/><xsl:param name="enqPast12Months"/><xsl:param name="noOfEnquiries"/><xsl:variable name="dateofEnquiry" select="string((Root/root/consumerCreditData/item/item/enquiries/item)[$noOfEnquiries]/enquiryDate)"></xsl:variable><xsl:variable name="daysDifference" select="usr:getDaysDifference($currentDate,usr:formatDate(string($dateofEnquiry)))"></xsl:variable><xsl:variable name="monthsDifference" select="usr:getMonthsDifference($currentDate,usr:formatDate(string($dateofEnquiry)))"></xsl:variable><xsl:choose><xsl:when test="string($noOfEnquiries) = '0'"><xsl:value-of select="$enqPast12Months"/>
			</xsl:when><xsl:otherwise>
			</xsl:otherwise></xsl:choose><xsl:if test="$noOfEnquiries >= 0"><xsl:call-template name="getEnqPast12Months"><xsl:with-param name="currentDate" select="$currentDate"/><xsl:with-param name="enqPast12Months"><xsl:choose><xsl:when test="($monthsDifference &lt;= 12) and ($daysDifference > 30)"><xsl:value-of select="$enqPast12Months + 1"></xsl:value-of></xsl:when><xsl:when test="$monthsDifference > 12"><xsl:value-of select="$enqPast12Months"></xsl:value-of></xsl:when><xsl:otherwise><xsl:value-of select="$enqPast12Months"></xsl:value-of></xsl:otherwise>
					</xsl:choose>
				</xsl:with-param><xsl:with-param name="noOfEnquiries" select="$noOfEnquiries - 1"/>
			</xsl:call-template>
		</xsl:if>
	</xsl:template><xsl:template name="getEnqPast24Months"><xsl:param name="currentDate"/><xsl:param name="enqPast24Months"/><xsl:param name="noOfEnquiries"/><xsl:variable name="dateofEnquiry" select="string((Root/root/consumerCreditData/item/item/enquiries/item)[$noOfEnquiries]/enquiryDate)"></xsl:variable><xsl:variable name="monthsDifference" select="usr:getMonthsDifference($currentDate,usr:formatDate(string($dateofEnquiry)))"></xsl:variable><xsl:choose><xsl:when test="string($noOfEnquiries) = '0'"><xsl:value-of select="$enqPast24Months"/>
      </xsl:when><xsl:otherwise>
      </xsl:otherwise></xsl:choose><xsl:if test="$noOfEnquiries >= 0"><xsl:call-template name="getEnqPast24Months"><xsl:with-param name="currentDate" select="$currentDate"/><xsl:with-param name="enqPast24Months"><xsl:choose><xsl:when test="($monthsDifference &lt;= 24) and ($monthsDifference > 12)"><xsl:value-of select="$enqPast24Months + 1"></xsl:value-of></xsl:when><xsl:when test="$monthsDifference > 24"><xsl:value-of select="$enqPast24Months"></xsl:value-of></xsl:when><xsl:otherwise><xsl:value-of select="$enqPast24Months"></xsl:value-of></xsl:otherwise>
          </xsl:choose>
        </xsl:with-param><xsl:with-param name="noOfEnquiries" select="$noOfEnquiries - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
-->

<!-- Gender Template -->
<xsl:template name="Getgender">
    <xsl:param name="gender"/>
    <xsl:if test="$gender = '02' or $gender = '2' or $gender = 'M'">
        <xsl:text>MALE</xsl:text>
    </xsl:if>
    <xsl:if test="$gender = '01' or $gender = '1' or $gender = 'F'">
        <xsl:text>FEMALE</xsl:text>
    </xsl:if>
    <xsl:if test="$gender = '03' or $gender = '3' or $gender = 'T'">
        <xsl:text>TRANSGENDER</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Gender Template end -->

<!-- Score Template-->
<xsl:template name="getScore">
    <xsl:param name="score"/>
    <xsl:choose>
        <xsl:when test="$score = '000-1' or $score = '-1'">
            <xsl:text>-1</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$score"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Score Template end -->

<!-- Date Process -->
<xsl:template name="formatDate">
    <xsl:param name="inpDate"/>
    <xsl:choose>
        <xsl:when test="normalize-space($inpDate) = ''">
            <xsl:text></xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="concat(substring($inpDate, 1,2),'-',substring($inpDate, 3,2),'-',substring($inpDate, 5))"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Date Process End  -->

<!-- Time Process    -->
<xsl:template name="formatTime">
    <xsl:param name="inpTime"/>
    <xsl:choose>
        <xsl:when test="normalize-space($inpTime) = ''">
            <xsl:text></xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="concat(substring($inpTime, 1,2),':',substring($inpTime, 3,2),':',substring($inpTime, 5,6))"/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Time Process End   -->

<!-- State code Function  -->
<xsl:template name="GetState">
    <xsl:param name="stCode"/>
    <xsl:choose>
        <xsl:when test="$stCode = null or $stCode = '' or $stCode = ' ' ">
            <xsl:text></xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:if test="$stCode='01' or $stCode='JK'">
                <xsl:text>JAMMU AND KASHMIR</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='02' or $stCode='HP'">
                <xsl:text>HIMACHAL PRADESH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='03' or $stCode='PB'">
                <xsl:text>PUNJAB</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='04' or $stCode='CH'">
                <xsl:text>CHANDIGARH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='05' or $stCode='UK'">
                <xsl:text>UTTARAKHAND</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='06' or $stCode='HR'">
                <xsl:text>HARYANA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='07' or $stCode='DL'">
                <xsl:text>DELHI</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='08' or $stCode='RJ'">
                <xsl:text>RAJASTHAN</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='09' or $stCode='UP'">
                <xsl:text>UTTAR PRADESH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='10' or $stCode='BR'">
                <xsl:text>BIHAR</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='11' or $stCode='SK'">
                <xsl:text>SIKKIM</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='12' or $stCode='AR'">
                <xsl:text>ARUNACHAL PRADESH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='13' or $stCode='NL'">
                <xsl:text>NAGALAND</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='14' or $stCode='MN'">
                <xsl:text>MANIPUR</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='15' or $stCode='MZ'">
                <xsl:text>MIZORAM</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='16' or $stCode='TR'">
                <xsl:text>TRIPURA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='17' or $stCode='ML'">
                <xsl:text>MEGHALAYA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='18' or $stCode='AS'">
                <xsl:text>ASSAM</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='19' or $stCode='WB'">
                <xsl:text>WEST BENGAL</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='20' or $stCode='JH'">
                <xsl:text>JHARKHAND</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='21' or $stCode='OR'">
                <xsl:text>ORISSA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='22' or $stCode='CH'">
                <xsl:text>CHHATTISGARH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='23' or $stCode='MP'">
                <xsl:text>MADHYA PRADESH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='24' or $stCode='GJ'">
                <xsl:text>GUJARAT</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='25' or $stCode='DD'">
                <xsl:text>DAMAN AND DIU</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='26' or $stCode='DN'">
                <xsl:text>DADRA AND NAGAR HAVELI</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='27' or $stCode='MH'">
                <xsl:text>MAHARASHTRA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='28' or $stCode='AP'">
                <xsl:text>ANDHRA PRADESH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='29' or $stCode='KA'">
                <xsl:text>KARNATAKA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='30' or $stCode='GA'">
                <xsl:text>GOA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='31' or $stCode='LD'">
                <xsl:text>LAKSHADWEEP</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='32' or $stCode='KL'">
                <xsl:text>KERALA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='33' or $stCode='TN'">
                <xsl:text>TAMIL NADU</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='34' or $stCode='PY'">
                <xsl:text>PONDICHERRY</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='35' or $stCode='AN'">
                <xsl:text>ANDAMAN AND NICOBAR ISLANDS</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='36' or $stCode='TS'">
                <xsl:text>TELANGANA</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='38' ">
                <xsl:text>LADAKH</xsl:text>
            </xsl:if>
            <xsl:if test="$stCode='99' ">
                <xsl:text>APO ADDRESS</xsl:text>
            </xsl:if>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- State code Function End -->


<!-- Template for ownership Indicator  -->
<xsl:template name="getOwnershipInd">
    <xsl:param name="ownerShipIndicator"/>
    <xsl:if test="$ownerShipIndicator = '1'">
        <xsl:text>INDIVIDUAL</xsl:text>
    </xsl:if>
    <xsl:if test="$ownerShipIndicator = '2'">
        <xsl:text>AUTHORISED USER</xsl:text>
    </xsl:if>
    <xsl:if test="$ownerShipIndicator = '3'">
        <xsl:text>GUARANTOR</xsl:text>
    </xsl:if>
    <xsl:if test="$ownerShipIndicator = '4'">
        <xsl:text>JOINT</xsl:text>
    </xsl:if>
	<xsl:if test="$ownerShipIndicator = '5'">
        <xsl:text>DECEASED</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Template for ownership Indicator End -->

<!-- Template For COLLATERAL TYPE -->
<xsl:template name="getCollateral">
    <xsl:param name="collId"/>
    <xsl:if test="$collId = '00'">
        <xsl:text>NO COLLATERAL</xsl:text>
    </xsl:if>
    <xsl:if test="$collId = '01'">
        <xsl:text>PROPERTY</xsl:text>
    </xsl:if>
    <xsl:if test="$collId = '02'">
        <xsl:text>GOLD</xsl:text>
    </xsl:if>
    <xsl:if test="$collId = '03'">
        <xsl:text>SHARES</xsl:text>
    </xsl:if>
    <xsl:if test="$collId = '04'">
        <xsl:text>SAVING ACCOUNT AND FIXED DEPOSIT</xsl:text>
    </xsl:if>
	<xsl:if test="$collId = '05'">
        <xsl:text>MULTIPLE SECURITIES</xsl:text>
    </xsl:if>
	<xsl:if test="$collId = '06'">
        <xsl:text>OTHERS</xsl:text>
    </xsl:if>
</xsl:template>

<!-- Template For COLLATERAL TYPE end-->

<!-- Templaye for Account type -->
<xsl:template name="getAccountType">
    <xsl:param name="id" />
    <xsl:if test="$id = '01'">
        <xsl:text>Auto Loan (Personal) </xsl:text>
    </xsl:if>
    <xsl:if test="$id = '02'">
        <xsl:text>HOUSING LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '03'">
        <xsl:text>PROPERTY LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '04'">
        <xsl:text>LOAN AGAINST SHARES/SECURITIES</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '05'">
        <xsl:text>PERSONAL LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '06'">
        <xsl:text>CONSUMER LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '07'">
        <xsl:text>GOLD LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '08'">
        <xsl:text>EDUCATION LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '09'">
        <xsl:text>LOAN TO PROFESSIONAL</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '10'">
        <xsl:text>CREDIT CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '11'">
        <xsl:text>LEASING</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '12'">
        <xsl:text>OVERDRAFT</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '13'">
        <xsl:text>TWO-WHEELER LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '14'">
        <xsl:text>NON-FUNDED CREDIT FACILITY</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '15'">
        <xsl:text>LOAN AGAINST BANK DEPOSITS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '16'">
        <xsl:text>FLEET CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '17'">
        <xsl:text>COMMERCIAL VEHICLE LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '18'">
        <xsl:text>TELCO – WIRELESS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '19'">
        <xsl:text>TELCO – BROADBAND</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '20'">
        <xsl:text>TELCO – LANDLINE</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '21'">
        <xsl:text>SELLER FINANCING</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '22'">
        <xsl:text>SELLER FINANCING SOFT</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '23'">
        <xsl:text>GECL LOAN SECURED</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '24'">
        <xsl:text>GECL LOAN UNSECURED</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '31'">
        <xsl:text>SECURED CREDIT CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '32'">
        <xsl:text>USED CAR LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '33'">
        <xsl:text>CONSTRUCTION EQUIPMENT LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '34'">
        <xsl:text>TRACTOR LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '35'">
        <xsl:text>CORPORATE CREDIT CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '36'">
        <xsl:text>KISAN CREDIT CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '37'">
        <xsl:text>LOAN ON CREDIT CARD</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '38'">
        <xsl:text>PRIME MINISTER JAAN DHAN YOJANA - OVERDRAFT</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '39'">
        <xsl:text>MUDRA LOANS – SHISHU / KISHOR / TARUN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '40'">
        <xsl:text>MICROFINANCE – BUSINESS LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '41'">
        <xsl:text>MICROFINANCE – PERSONAL LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '42'">
        <xsl:text>MICROFINANCE – HOUSING LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '43'">
        <xsl:text>MICROFINANCE – OTHER</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '44'">
        <xsl:text>PRADHAN MANTRI AWAS YOJANA - CREDIT LINK SUBSIDY SCHEME MAY CLSS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '50'">
        <xsl:text>BUSINESS LOAN – SECURED</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '51'">
        <xsl:text>BUSINESS LOAN – GENERAL</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '52'">
        <xsl:text>BUSINESS LOAN – PRIORITY SECTOR – SMALL BUSINESS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '53'">
        <xsl:text>BUSINESS LOAN – PRIORITY SECTOR – AGRICULTURE</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '54'">
        <xsl:text>BUSINESS LOAN – PRIORITY SECTOR – OTHERS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '55'">
        <xsl:text>BUSINESS NON-FUNDED CREDIT FACILITY – GENERAL</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '56'">
        <xsl:text>BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR – SMALL BUSINESS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '57'">
        <xsl:text>BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR – AGRICULTURE</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '58'">
        <xsl:text>BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR-OTHERS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '59'">
        <xsl:text>BUSINESS LOAN AGAINST BANK DEPOSITS</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '61'">
        <xsl:text>BUSINESS LOAN - UNSECURED</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '80'">
        <xsl:text>MICROFINANCE DETAILED REPORT (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '81'">
        <xsl:text>SUMMARY REPORT (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '88'">
        <xsl:text>LOCATE PLUS FOR INSURANCE (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '90'">
        <xsl:text>ACCOUNT REVIEW (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '91'">
        <xsl:text>RETRO ENQUIRY (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '92'">
        <xsl:text>LOCATE PLUS (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '97'">
        <xsl:text>ADVISER LIABILITY (APPLICABLE TO ENQUIRY PURPOSE ONLY)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '00'">
        <xsl:text>OTHER</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '98'">
        <xsl:text>SECURED (ACCOUNT GROUP FOR PORTFOLIO REVIEW RESPONSE)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '99'">
        <xsl:text>UNSECURED (ACCOUNT GROUP FOR PORTFOLIO REVIEW RESPONSE)</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '45'">
        <xsl:text>P2P PERSONAL LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '46'">
        <xsl:text>P2P AUTO LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id = '47'">
        <xsl:text>P2P EDUCATION LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$id='66'">
        <xsl:text>EXPRESS MATCH - NEW LOAN APPLICATION</xsl:text>
    </xsl:if>
    <xsl:if test="$id='69'">
        <xsl:text>SHORT TERM PERSONAL LOAN</xsl:text>
    </xsl:if>
	<xsl:if test="$id='70'">
        <xsl:text>PRIORITY SECTOR - GOLD LOAN</xsl:text>
    </xsl:if>
	<xsl:if test="$id='71'">
        <xsl:text>TEMPORARY OVERDRAFT</xsl:text>
    </xsl:if>
	<xsl:if test="$id='67'">
        <xsl:text>Buy Now Pay Later</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Templaye for Account type End-->



<!-- Template for Accound dispute -->
<xsl:template name="getAccountDisputeDesc">
    <xsl:param name="disputeId"/>
    <xsl:if test="$disputeId ='000'">
        <xsl:text>NO DISPUTES</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='003'">
        <xsl:text>ACCOUNT NUMBER IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='004'">
        <xsl:text>ACCOUNT TYPE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='005'">
        <xsl:text>OWNERSHIP INDICATOR IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='008'">
        <xsl:text>DATE OPENED/DISBURSED IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='009'">
        <xsl:text>DATE OF LAST PAYMENT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='010'">
        <xsl:text>DATE CLOSED IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='011'">
        <xsl:text>DATE REPORTED AND CERTIFIED IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='012'">
        <xsl:text>HIGH CREDIT/SANCTIONED AMOUNT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='013'">
        <xsl:text>CURRENT BALANCE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='014'">
        <xsl:text>AMOUNT OVERDUE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='030'">
        <xsl:text>PAYMENT HISTORY START DATE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='031'">
        <xsl:text>PAYMENT HISTORY END DATE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='032'">
        <xsl:text>SUIT FILED / WILFUL DEFAULT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='033'">
        <xsl:text>WRITTEN-OFF AND SETTLED STATUS IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='034'">
        <xsl:text>VALUE OF COLLATERAL IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='035'">
        <xsl:text>TYPE OF COLLATERAL IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='036'">
        <xsl:text>CREDIT LIMIT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='037'">
        <xsl:text>CASH LIMIT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='038'">
        <xsl:text>RATE OF INTEREST IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='039'">
        <xsl:text>REPAYMENT TENURE IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='040'">
        <xsl:text>EMI AMOUNT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='041'">
        <xsl:text>WRITTEN-OFF AMOUNT (TOTAL) IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='042'">
        <xsl:text>WRITTEN-OFF AMOUNT (PRINCIPAL) IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='043'">
        <xsl:text>SETTLEMENT AMOUNT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='044'">
        <xsl:text>PAYMENT FREQUENCY IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='045'">
        <xsl:text>ACTUAL PAYMENT AMOUNT IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='101'">
        <xsl:text>PAYMENT HISTORY 1 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='102'">
        <xsl:text>PAYMENT HISTORY 2 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='103'">
        <xsl:text>PAYMENT HISTORY 3 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='104'">
        <xsl:text>PAYMENT HISTORY 4 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='105'">
        <xsl:text>PAYMENT HISTORY 5 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='106'">
        <xsl:text>PAYMENT HISTORY 6 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='107'">
        <xsl:text>PAYMENT HISTORY 7 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='108'">
        <xsl:text>PAYMENT HISTORY 8 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='109'">
        <xsl:text>PAYMENT HISTORY 9 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='110'">
        <xsl:text>PAYMENT HISTORY 10 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='111'">
        <xsl:text>PAYMENT HISTORY 11 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='112'">
        <xsl:text>PAYMENT HISTORY 12 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='113'">
        <xsl:text>PAYMENT HISTORY 13 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='114'">
        <xsl:text>PAYMENT HISTORY 14 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='115'">
        <xsl:text>PAYMENT HISTORY 15 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='116'">
        <xsl:text>PAYMENT HISTORY 16 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='117'">
        <xsl:text>PAYMENT HISTORY 17 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='118'">
        <xsl:text>PAYMENT HISTORY 18 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='119'">
        <xsl:text>PAYMENT HISTORY 19 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='120'">
        <xsl:text>PAYMENT HISTORY 20 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='121'">
        <xsl:text>PAYMENT HISTORY 21 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='122'">
        <xsl:text>PAYMENT HISTORY 22 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='123'">
        <xsl:text>PAYMENT HISTORY 23 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='124'">
        <xsl:text>PAYMENT HISTORY 24 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='125'">
        <xsl:text>PAYMENT HISTORY 25 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='126'">
        <xsl:text>PAYMENT HISTORY 26 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='127'">
        <xsl:text>PAYMENT HISTORY 27 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='128'">
        <xsl:text>PAYMENT HISTORY 28 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='129'">
        <xsl:text>PAYMENT HISTORY 29 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='130'">
        <xsl:text>PAYMENT HISTORY 30 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='131'">
        <xsl:text>PAYMENT HISTORY 31 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='132'">
        <xsl:text>PAYMENT HISTORY 32 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='133'">
        <xsl:text>PAYMENT HISTORY 33 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='134'">
        <xsl:text>PAYMENT HISTORY 34 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='135'">
        <xsl:text>PAYMENT HISTORY 35 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='136'">
        <xsl:text>PAYMENT HISTORY 36 IN DISPUTE</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='203'">
        <xsl:text>ACCOUNT NUMBER - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='204'">
        <xsl:text>ACCOUNT TYPE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='205'">
        <xsl:text>OWNERSHIP INDICATOR - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='208'">
        <xsl:text>DATE OPENED/DISBURSED - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='209'">
        <xsl:text>DATE OF LAST PAYMENT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='210'">
        <xsl:text>DATE CLOSED - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='211'">
        <xsl:text>DATE REPORTED AND CERTIFIED - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='212'">
        <xsl:text>HIGH CREDIT/SANCTIONED AMOUNT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='213'">
        <xsl:text>CURRENT BALANCE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='214'">
        <xsl:text>AMOUNT OVERDUE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='230'">
        <xsl:text>PAYMENT HISTORY START DATE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='231'">
        <xsl:text>PAYMENT HISTORY END DATE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='232'">
        <xsl:text>SUIT FILED / WILFUL DEFAULT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='233'">
        <xsl:text>WRITTEN-OFF AND SETTLED STATUS - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='234'">
        <xsl:text>VALUE OF COLLATERAL - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='235'">
        <xsl:text>TYPE OF COLLATERAL - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='236'">
        <xsl:text>CREDIT LIMIT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='237'">
        <xsl:text>CASH LIMIT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='238'">
        <xsl:text>RATE OF INTEREST - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='239'">
        <xsl:text>REPAYMENT TENURE - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='240'">
        <xsl:text>EMI AMOUNT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='241'">
        <xsl:text>WRITTEN-OFF AMOUNT (TOTAL) - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='242'">
        <xsl:text>WRITTEN-OFF AMOUNT (PRINCIPAL) - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='243'">
        <xsl:text>SETTLEMENT AMOUNT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='244'">
        <xsl:text>PAYMENT FREQUENCY - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='245'">
        <xsl:text>ACTUAL PAYMENT AMOUNT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='301'">
        <xsl:text>PAYMENT HISTORY 1 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='302'">
        <xsl:text>PAYMENT HISTORY 2 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='303'">
        <xsl:text>PAYMENT HISTORY 3 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='304'">
        <xsl:text>PAYMENT HISTORY 4 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='305'">
        <xsl:text>PAYMENT HISTORY 5 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='306'">
        <xsl:text>PAYMENT HISTORY 6 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='307'">
        <xsl:text>PAYMENT HISTORY 7 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='308'">
        <xsl:text>PAYMENT HISTORY 8 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='309'">
        <xsl:text>PAYMENT HISTORY 9 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='310'">
        <xsl:text>PAYMENT HISTORY 10 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='311'">
        <xsl:text>PAYMENT HISTORY 11 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='312'">
        <xsl:text>PAYMENT HISTORY 12 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='313'">
        <xsl:text>PAYMENT HISTORY 13 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='314'">
        <xsl:text>PAYMENT HISTORY 14 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='315'">
        <xsl:text>PAYMENT HISTORY 15 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='316'">
        <xsl:text>PAYMENT HISTORY 16 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='317'">
        <xsl:text>PAYMENT HISTORY 17 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='318'">
        <xsl:text>PAYMENT HISTORY 18 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='319'">
        <xsl:text>PAYMENT HISTORY 19 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='320'">
        <xsl:text>PAYMENT HISTORY 20 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='321'">
        <xsl:text>PAYMENT HISTORY 21 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='322'">
        <xsl:text>PAYMENT HISTORY 22 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='323'">
        <xsl:text>PAYMENT HISTORY 23 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='324'">
        <xsl:text>PAYMENT HISTORY 24 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='325'">
        <xsl:text>PAYMENT HISTORY 25 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='326'">
        <xsl:text>PAYMENT HISTORY 26 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='327'">
        <xsl:text>PAYMENT HISTORY 27 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='328'">
        <xsl:text>PAYMENT HISTORY 28 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='329'">
        <xsl:text>PAYMENT HISTORY 29 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='330'">
        <xsl:text>PAYMENT HISTORY 30 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='331'">
        <xsl:text>PAYMENT HISTORY 31 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='332'">
        <xsl:text>PAYMENT HISTORY 32 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='333'">
        <xsl:text>PAYMENT HISTORY 33 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='334'">
        <xsl:text>PAYMENT HISTORY 34 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='335'">
        <xsl:text>PAYMENT HISTORY 35 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='336'">
        <xsl:text>PAYMENT HISTORY 36 - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='885'">
        <xsl:text>DUPLICATE ACCOUNT - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='886'">
        <xsl:text>DUPLICATE ACCOUNT</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='887'">
        <xsl:text>ACCOUNT OWNERSHIP ERROR - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='888'">
        <xsl:text>ACCOUNT OWNERSHIP ERROR</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='998'">
        <xsl:text>MULTIPLE DISPUTES - DISPUTE ACCEPTED - PENDING CORRECTIONS BY THE MEMBER</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId ='999'">
        <xsl:text>MULTIPLE DISPUTES</xsl:text>
    </xsl:if>
    <xsl:if test="$disputeId =''">
        <xsl:text></xsl:text>
    </xsl:if>
</xsl:template>
<!-- Template for Accound dispute End -->



<xsl:template name="getEmploymentDisputeDesc">
    <xsl:param name="empDisputeId"/>
    <xsl:if test="$empDisputeId='000001'">
        <xsl:text>Disputed accepted – under investigation</xsl:text>
    </xsl:if>
    <xsl:if test="$empDisputeId=''">
        <xsl:text></xsl:text>
    </xsl:if>
</xsl:template>


<!-- Template Scoreing Factor Exclusion Reason code -->
<xsl:template name="getExclusionReason">
    <xsl:param name="id"/>
    <xsl:param name="counter"/>
    <xsl:if test="$counter ='1' and $id ='01'">
        <xsl:text>One or more trades with suit filed status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='2' and $id ='01'">
        <xsl:text>One or more trades with wilful default status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='3' and $id ='01'">
        <xsl:text>One or more trades with suit filed (wilful default) status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='4' and $id ='01'">
        <xsl:text>One or more trades written off in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='5' and $id ='01'">
        <xsl:text>One or more trades with suit filed and written off status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='6' and $id ='01'">
        <xsl:text>One or more trades with wilful default and written off status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='7' and $id ='01'">
        <xsl:text>One or more trades with suit filed (wilful default) and written off status in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='8' and $id ='01'">
        <xsl:text>No eligible trade for scoring.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='9' and $id ='01'">
        <xsl:text>One or more trades with restructured debt in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='10' and $id = '01'">
        <xsl:text>One or more trades with settled debt in the past 24 months.</xsl:text>
    </xsl:if>
    <xsl:if test="$counter ='' or $id = ''">
        <xsl:text>Refer TUEF Guide</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Template Scoreing Factor Exclusion reason code End-->


<!-- Template Scoreing Factor Reason code -->
<xsl:template name ="getReasonCodeDescription">
    <xsl:param name="id"/>
    <xsl:param name="scoretype"/>
    <xsl:choose>
        <xsl:when test="$scoretype='01'">
            <xsl:if test="$id=''">
                <xsl:text></xsl:text>
            </xsl:if>
            <xsl:if test="$id ='01'">
                <xsl:text>Too many tradelines 91+ days delinquent in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='02'">
                <xsl:text>Presence of a tradeline 91+ days delinquent in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='03'">
                <xsl:text>Credit card balances are too high in proportion to High Credit Amount</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='04'">
                <xsl:text>Too many tradelines with worst status in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='05'">
                <xsl:text>Presence of severe delinquency in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='06'">
                <xsl:text>Presence of a minor delinquency in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='07'">
                <xsl:text>Presence of a tradeline with worst status in the past 6 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='08'">
                <xsl:text>Credit card balances are high in proportion to High Credit Amount</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='09'">
                <xsl:text>High number of trades with low proportion of satisfactory trades</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='10'">
                <xsl:text>Low proportion of satisfactory trades</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='11'">
                <xsl:text>No presence of a  revolving tradeline</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='12'">
                <xsl:text>Presence of a tradeline 91+ days delinquent  7 to 12 months ago</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='13'">
                <xsl:text>Low average trade age</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='14'">
                <xsl:text>Presence of a tradeline 91+ days delinquent 13 or more months ago</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='15'">
                <xsl:text>Presence of a minor delinquency  7 to 12 months ago</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='16'">
                <xsl:text>Presence of a severe delinquency  7 to 12 months ago</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='17'">
                <xsl:text>Presence of a high number of enquiries</xsl:text>
            </xsl:if>
        </xsl:when>
        <xsl:when test="$scoretype='04'">
            <xsl:if test="$id=''">
                <xsl:text></xsl:text>
            </xsl:if>
            <xsl:if test="$id ='01'">
                <xsl:text>Not enough credit card debt experience</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='02'">
                <xsl:text>Length of time since most recent account delinquency is too short</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='03'">
                <xsl:text>Too many two-wheeler accounts</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='04'">
                <xsl:text>Too many business loans</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='05'">
                <xsl:text>Credit card account balances too high in proportion to credit limits</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='06'">
                <xsl:text>Maximum amount on mortgage loan is low</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='07'">
                <xsl:text>Total amount past due is too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='08'">
                <xsl:text>Not enough mortgage debt experience</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='09'">
                <xsl:text>Too much change of indebtedness on non-mortgage trades over the past 24 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='10'">
                <xsl:text>Insufficient improvement in delinquency status</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='11'">
                <xsl:text>Too much increase of indebtedness on non-mortgage trades over the past 12 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='12'">
                <xsl:text>Too many enquiries</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='13'">
                <xsl:text>Too many accounts with a balance</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='14'">
                <xsl:text>Length of time accounts have been established is too short</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='15'">
                <xsl:text>Not enough debt experience</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='16'">
                <xsl:text>Too many credit card accounts</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='17'">
                <xsl:text>Too many Personal Loan enquiries</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='18'">
                <xsl:text>Number of active trades with a balance too high in proportion to total trades</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='19'">
                <xsl:text>Too much change of indebtedness on credit cards over the past 24 months</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='20'">
                <xsl:text>Credit card balance too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='21'">
                <xsl:text>Proportion of delinquent trades too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='22'">
                <xsl:text>Double check Customer Name, Address and KYC Credentials and Proceed</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='23'">
                <xsl:text>To be Rejected</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='24'">
                <xsl:text>Average</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='25'">
                <xsl:text>Poor Credit History</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='26'">
                <xsl:text>Good</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='27'">
                <xsl:text>Excellent</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='28'">
                <xsl:text>Invalid CIBIL Score</xsl:text>
            </xsl:if>
        </xsl:when>
        <xsl:when test="$scoretype='08'">
            <xsl:if test="$id=''">
                <xsl:text></xsl:text>
            </xsl:if>
            <xsl:if test="$id ='01'">
                <xsl:text> LOW CREDIT AGE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='02'">
                <xsl:text> PRESENCE OF DELINQUENCY IN LAST 12 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='03'">
                <xsl:text> PRESENCE OF DELINQUENCY IN THE RECENT PAST</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='04'">
                <xsl:text> LOW PROPORTION OF SATISFACTORY TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='05'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='06'">
                <xsl:text> HIGH BALANCE BUILD-UP ON SECURED LOANS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='07'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='08'">
                <xsl:text> PRESENCE OF SEVERE DELINQUENCY AS OF RECENT UPDATE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='09'">
                <xsl:text> HIGH BALANCE BUILD-UP</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='10'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='11'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='12'">
                <xsl:text> PRESENCE OF DELINQUENCY AS OF RECENT UPDATE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='13'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='14'">
                <xsl:text> INCREASE IN NON-MORTGAGE INDEBTEDNESS IN LAST 12 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='15'">
                <xsl:text> INCREASE IN NON-MORTGAGE INDEBTEDNESS IN LAST 3 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='16'">
                <xsl:text> HIGH BALANCE BUILD-UP</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='17'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='18'">
                <xsl:text> HIGH OUTSTANDING BALANCE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='19'">
                <xsl:text> INCREASE IN NON-MORTGAGE INDEBTEDNESS IN LAST 12 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='20'">
                <xsl:text> LENGTH OF TIME SINCE SEVERE DELINQUENCY IS TOO SHORT</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='21'">
                <xsl:text> LOW PROPORTION OF SATISFACTORY TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='22'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='23'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='24'">
                <xsl:text> LOW CREDIT AGE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='25'">
                <xsl:text> HIGH BALANCE BUILD-UP ON NON-MORTGAGE LOANS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='26'">
                <xsl:text> PRESENCE OF SEVERE DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='27'">
                <xsl:text> PRESENCE OF HIGH CREDIT ACTIVITY (INQUIRIES)</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='28'">
                <xsl:text> LOW CREDIT AGE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='29'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='30'">
                <xsl:text> LENGTH OF TIME SINCE MODERATE TO SEVERE DELINQUENCY IS TOO SHORT</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='31'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='32'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='33'">
                <xsl:text> HIGH PROPORTION OF DELINQUENT TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='34'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='35'">
                <xsl:text> PRESENCE OF DELINQUENCY</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='36'">
                <xsl:text> HIGH BALANCE BUILD-UP ON REVOLVING TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='37'">
                <xsl:text> PRESENCE OF DELINQUENCY AS OF RECENT UPDATE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='38'">
                <xsl:text> RECENT HIGH BALANCE BUILD ON BANKCARD TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='39'">
                <xsl:text> HIGH PROPORTION OF OUTSTANDING TRADES</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='40'">
                <xsl:text> HIGH BALANCE IN PROPORTION TO HIGH CREDIT AMOUNT IN THE LAST 12 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='41'">
                <xsl:text> PAYMENT MADE IN PROPORTION TO TOTAL CARD BALANCE OUTSTANDING IS LOW</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='42'">
                <xsl:text> PAYMENT MADE IN PROPORTION TO TOTAL BALANCE OUTSTANDING IS LOW</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='43'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='44'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='45'">
                <xsl:text> HIGH BALANCE BUILD-UP ON NON-MORTGAGE LOANS IN PAST 6 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='46'">
                <xsl:text> HIGH BALANCE BUILD-UP ON UNSECURED LOANS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='47'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='48'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='49'">
                <xsl:text> PRESENCE OF DELINQUENCY AS OF RECENT UPDATE</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='50'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='51'">
                <xsl:text> SUPPRESS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='52'">
                <xsl:text> PRESENCE OF MINOR DELINQUENCY IN LAST 24 MONTHS</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='53'">
                <xsl:text> PRESENCE OF SEVERE DELINQUENCY IN LAST 12 MONTHS</xsl:text>
            </xsl:if>
        </xsl:when>
        <xsl:when test="$scoretype='02'">
            <xsl:if test="$id=''">
                <xsl:text></xsl:text>
            </xsl:if>
            <xsl:if test="$id ='08'">
                <xsl:text>Credit card balances are high in proportion to High Credit Amount</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='10'">
                <xsl:text>Low proportion of satisfactory trades</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='13'">
                <xsl:text>Low average trade age</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='17'">
                <xsl:text>Presence of a high number of enquiries</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='18'">
                <xsl:text>Over due amount too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='19'">
                <xsl:text>Not enough available credit</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='20'">
                <xsl:text>Too few satisfactory bankcard accounts</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='21'">
                <xsl:text>Total balance of delinquencies is too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='22'">
                <xsl:text>Presence of delinquency</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='23'">
                <xsl:text>Total high credit of delinquencies is too high</xsl:text>
            </xsl:if>
            <xsl:if test="$id ='24'">
                <xsl:text>Presence of a minor delinquency on personal loan</xsl:text>
            </xsl:if>
        </xsl:when>
    </xsl:choose>
</xsl:template>
<!-- Template Scoreing Factor reason code End-->


<xsl:template name="getCurrentDate">
    <xsl:param name="rptDate"/>
    <xsl:call-template name="formatDate">
        <xsl:with-param name="inpDate" select="$rptDate"/>
    </xsl:call-template>
</xsl:template>


<!-- Template for suit Filed -->
<xsl:template name="getSuitFileorWilfulDefault">
    <xsl:param name="suiteId"/>
    <xsl:if test="$suiteId='00'">
        <xsl:text>NO SUIT FILED</xsl:text>
    </xsl:if>
    <xsl:if test="$suiteId='01'">
        <xsl:text>SUIT FILED</xsl:text>
    </xsl:if>
    <xsl:if test="$suiteId='02'">
        <xsl:text>WILFUL DEFAULT</xsl:text>
    </xsl:if>
    <xsl:if test="$suiteId='03'">
        <xsl:text>SUIT FILED (WILFUL DEFAULT)</xsl:text>
    </xsl:if>
    <xsl:if test="$suiteId=''">
        <xsl:text>Refer TUEF Guide</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Template for suit Filed End -->


<!-- Template for Written Off Settled Status -->

<xsl:template name="getWrittenOffSettledStatus">
    <xsl:param name="woStId"/>
    <xsl:if test="$woStId ='00'">
        <xsl:text> RESTRUCTURED LOAN</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='01'">
        <xsl:text> RESTRUCTURED LOAN (GOVT. MANDATED)</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='02'">
        <xsl:text> WRITTEN-OFF</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='03'">
        <xsl:text> SETTLED</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='04'">
        <xsl:text> POST (WO) SETTLED</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='05'">
        <xsl:text> ACCOUNT SOLD</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='06'">
        <xsl:text> WRITTEN OFF AND ACCOUNT SOLD</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='07'">
        <xsl:text> ACCOUNT PURCHASED</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='08'">
        <xsl:text> ACCOUNT PURCHASED AND WRITTEN OFF</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='09'">
        <xsl:text> ACCOUNT PURCHASED AND SETTLED</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='10'">
        <xsl:text> ACCOUNT PURCHASED AND RESTRUCTURED</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='11'">
        <xsl:text> RESTRUCTURED DUE TO NATURAL CALAMITY</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId ='12'">
        <xsl:text> RESTRUCTURED DUE TO COVID-19</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='13'">
        <xsl:text> POST WRITE OFF CLOSED</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='14'">
        <xsl:text> RESTRUCTURED and CLOSED</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='15'">
        <xsl:text> AUCTIONED and SETTLED</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='16'">
        <xsl:text> REPOSSESSED and SETTLED</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='17'">
        <xsl:text> GUARANTEE INVOKED</xsl:text>
    </xsl:if>
	<xsl:if test="$woStId ='99'">
        <xsl:text> CLEAR EXISTING STATUS</xsl:text>
    </xsl:if>
    <xsl:if test="$woStId=''">
        <xsl:text>Refer TUEF Guide</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Template for Written Off Settled Status -->

	  
<xsl:template name="dateFormatterForComparison">
    <xsl:param name="startDate" />
    <xsl:param name="duration" />
    <xsl:variable name="enquiryStartDate">
        <xsl:value-of select="concat(substring($startDate, 5,4),substring($startDate, 3,2),substring($startDate, 1,2))" />
    </xsl:variable>
    <xsl:variable name="enquiryEndDate">
        <xsl:if test="$duration != '' and $duration = 1">
            <xsl:variable name="enquiryEndMonth">
                <xsl:if test="substring($enquiryStartDate, 5,2) = '01'">
                    <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,12)" />
                </xsl:if>
                <xsl:if
						test="substring($enquiryStartDate, 5,2) &gt; 1 and substring($enquiryStartDate, 5,2) &lt; 10">
                    <xsl:value-of
							select="concat(substring($enquiryStartDate, 1,4),'0',(substring($enquiryStartDate, 5,2))-1)" />
                </xsl:if>
                <xsl:if test="substring($enquiryStartDate, 5,2) &gt;= 10">
                    <xsl:value-of
							select="concat(substring($enquiryStartDate, 1,4),(substring($enquiryStartDate, 5,2))-1)" />
                </xsl:if>
            </xsl:variable>
            <xsl:value-of
					select="concat($enquiryEndMonth,substring($enquiryStartDate, 7))" />
        </xsl:if>
        <xsl:if test="$duration != '' and $duration = 12">
            <xsl:variable name="enquiryEndMonth">
                <xsl:value-of
						select="concat((substring($startDate, 5))-1,substring($startDate, 3,2))" />
            </xsl:variable>
            <xsl:value-of select="concat($enquiryEndMonth,substring($startDate, 1,2))" />
        </xsl:if>
        <xsl:if test="$duration != '' and $duration = 24">
            <xsl:variable name="enquiryEndMonth">
                <xsl:value-of
						select="concat((substring($startDate, 5))-2,substring($startDate, 3,2))" />
            </xsl:variable>
            <xsl:value-of select="concat($enquiryEndMonth,substring($startDate, 1,2))" />
        </xsl:if>
        <xsl:if test="$duration != '' and $duration = 36">
            <xsl:variable name="enquiryEndMonth">
                <xsl:value-of
						select="concat((substring($startDate, 5))-3,(substring($startDate, 3,2))+1)" />
            </xsl:variable>
            <xsl:value-of select="concat($enquiryEndMonth,substring($startDate, 1,2))" />
        </xsl:if>
        <xsl:if test="$duration != '' and $duration = '60D'">
            <xsl:variable name="enquiryEndMonth">
                <xsl:if
						test="substring($enquiryStartDate, 5,2) = 1 or substring($enquiryStartDate, 5,2) = '01'">
                    <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,11)" />
                </xsl:if>
                <xsl:if
						test="substring($enquiryStartDate, 5,2) = 2 or substring($enquiryStartDate, 5,2) = '02'">
                    <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,12)" />
                </xsl:if>
                <xsl:if
						test="substring($enquiryStartDate, 5,2) &gt; 2 and substring($enquiryStartDate, 5,2) &lt;= 11">
                    <xsl:value-of
							select="concat(substring($enquiryStartDate, 1,4),'0',(substring($enquiryStartDate, 5,2))-2)" />
                </xsl:if>
                <xsl:if test="substring($enquiryStartDate, 5,2)=12">
                    <xsl:value-of
							select="concat(substring($enquiryStartDate, 1,4),(substring($enquiryStartDate, 5,2))-2)" />
                </xsl:if>
            </xsl:variable>
            <xsl:value-of
					select="concat($enquiryEndMonth,substring($enquiryStartDate, 7))" />
        </xsl:if>
    </xsl:variable>
    <xsl:value-of select="$enquiryEndDate" />
</xsl:template>
<xsl:template name="recursiveDateFormatForComparison">
    <xsl:param name="startDate" />
    <xsl:param name="duration" />
    <xsl:param name="counter" />
    <xsl:param name="endDate" />
    <xsl:param name="lastProcessedPosition" />
    <xsl:variable name="numberOfEnquiries">
        <xsl:value-of
					select="count(//Root/root/consumerCreditData/item/enquiries)" />
    </xsl:variable>
    <xsl:if test="$startDate != ''  and $duration != ''">
        <xsl:variable name="enquiryStartDate">
            <xsl:value-of select="concat(substring($startDate, 5,4),substring($startDate, 3,2),substring($startDate, 1,2))" />
        </xsl:variable>
        <xsl:variable name="enquiryEndDate">
            <xsl:if test="$duration != '' and $duration = 1">
                <xsl:variable name="enquiryEndMonth">
                    <xsl:if test="substring($enquiryStartDate, 5,2) = 01">
                        <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,12)" />
                    </xsl:if>
                    <xsl:if test="substring($enquiryStartDate, 5,2) &gt; 01">
                        <xsl:value-of
								select="concat(substring($enquiryStartDate, 1,4),(substring($enquiryStartDate, 5,2))-1)" />
                    </xsl:if>
                </xsl:variable>
                <xsl:value-of
						select="concat($enquiryEndMonth,substring($enquiryStartDate, 7))" />
            </xsl:if>
            <xsl:if test="$duration != '' and $duration = 12">
                <xsl:variable name="enquiryEndMonth">
                    <xsl:value-of
							select="concat((substring($startDate, 5))-1,substring($startDate, 3,2))" />
                </xsl:variable>
                <xsl:value-of select="concat($enquiryEndMonth,substring($startDate, 1,2))" />
            </xsl:if>
            <xsl:if test="$duration != '' and $duration = 24">
                <xsl:variable name="enquiryEndMonth">
                    <xsl:value-of
							select="concat((substring($startDate, 5))-2,substring($startDate, 3))" />
                </xsl:variable>
            </xsl:if>
            <xsl:if test="$duration != '' and $duration = '60D'">
                <xsl:variable name="enquiryEndMonth">
                    <xsl:if test="substring($enquiryStartDate, 3,2) = 02">
                        <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,12)" />
                    </xsl:if>
                    <xsl:if test="substring($enquiryStartDate, 3,2) = 01">
                        <xsl:value-of select="concat((substring($enquiryStartDate, 1,4))-1,11)" />
                    </xsl:if>
                    <xsl:if test="substring($enquiryStartDate, 3,2) &gt; 01 and substring($enquiryStartDate, 3,2) &lt;= 11">
                        <xsl:value-of
								select="concat(substring($enquiryStartDate, 1,4),'0',(substring($enquiryStartDate, 3,2))-2)" />
                    </xsl:if>
                    <xsl:if test="substring($enquiryStartDate, 3,2)=12">
                        <xsl:value-of
								select="concat(substring($enquiryStartDate, 1,4),(substring($enquiryStartDate, 3,2))-2)" />
                    </xsl:if>
                </xsl:variable>
                <xsl:value-of
						select="concat($enquiryEndMonth,substring($enquiryStartDate, 7))" />
            </xsl:if>
        </xsl:variable>
        <xsl:variable name="dateToCompare">
            <xsl:variable name="dateVar">
                <xsl:value-of select="//Root/root/consumerCreditData/item/enquiries[$lastProcessedPosition]/enquiryDate" />
            </xsl:variable>
            <xsl:value-of
						select="concat(substring($dateVar, 5),substring($dateVar, 3,2),substring($dateVar, 1,2))" />
        </xsl:variable>
        <xsl:variable name="recursiveStartDate">
            <xsl:value-of
						select="//Root/root/consumerCreditData/item/enquiries[$lastProcessedPosition]/enquiryDate" />
        </xsl:variable>
        <xsl:choose>
            <xsl:when
					test="$enquiryStartDate &gt;= $dateToCompare and $dateToCompare &gt;= $endDate and $lastProcessedPosition &lt;= $numberOfEnquiries">
                <xsl:call-template name="recursiveDateFormatForComparison">
                    <xsl:with-param name="startDate" select="$recursiveStartDate" />
                    <xsl:with-param name="duration" select="$duration" />
                    <xsl:with-param name="counter" select="($counter)+1" />
                    <xsl:with-param name="endDate" select="$endDate" />
                    <xsl:with-param name="lastProcessedPosition"
							select="($lastProcessedPosition)+1" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:if test="$lastProcessedPosition &lt; $numberOfEnquiries">
                    <xsl:call-template name="recursiveDateFormatForComparison">
                        <xsl:with-param name="startDate" select="$recursiveStartDate" />
                        <xsl:with-param name="duration" select="$duration" />
                        <xsl:with-param name="counter" select="$counter" />
                        <xsl:with-param name="endDate" select="$endDate" />
                        <xsl:with-param name="lastProcessedPosition"
								select="($lastProcessedPosition)+1" />
                    </xsl:call-template>
                </xsl:if>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:if>
    <xsl:if test="$lastProcessedPosition = $numberOfEnquiries">
        <xsl:value-of select="$counter" />
    </xsl:if>
</xsl:template>


<!-- Templay For CV Description ( Bureau charaterstics) -->

<xsl:template name="getCVDescription">
    <xsl:param name="cvId"/>
    <xsl:if test="$cvId=''">
        <xsl:text></xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BC_TRD'">
        <xsl:text>Number of bankcard trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='INST_TRD'">
        <xsl:text>Number of installment trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='NON_MT_TRD'">
        <xsl:text>Number of non-mortgage trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRD'">
        <xsl:text>TotalNoOfAllAccounts</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='UL_TRD'">
        <xsl:text>Number of unsecured loan trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG901'">
        <xsl:text>Non-Mortgage Balance Increases over the last Quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG902'">
        <xsl:text>Non-Mortgage Balance Decreases over the last Quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG905'">
        <xsl:text>Aggregate bankcard utilization average over the last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG906'">
        <xsl:text>Aggregate bankcard utilization average over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG907'">
        <xsl:text>Max aggregate bankcard balance over the last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG908'">
        <xsl:text>Max aggregate bankcard balance over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG909'">
        <xsl:text>Months since max aggregate bankcard balance over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG910'">
        <xsl:text>Max aggregate bankcard utilization over the last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG911'">
        <xsl:text>Max aggregate bankcard utilization over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BALMAG01'">
        <xsl:text>Non-Mortgage Balance Build-Up Behaviour [Higher the Value, higher the RISK]</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BALMAG03'">
        <xsl:text>Cards balance magnitude</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT01'">
        <xsl:text>Number of installment events prepaying in last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT02'">
        <xsl:text>Number of installment events prepaying in last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT03'">
        <xsl:text>Total amount prepaid on installment last month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT04'">
        <xsl:text>Total amount prepaid on installment in last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT05'">
        <xsl:text>Total amount prepaid on installment in last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT09'">
        <xsl:text>Bankcard ratio actual to min pay over last month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT10'">
        <xsl:text>Number of payments in last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT11'">
        <xsl:text>Number of payments in last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT50'">
        <xsl:text>Number of required payments in last month for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT51'">
        <xsl:text>Number of Required payments in last 3 months for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT52'">
        <xsl:text>Number of Required payments in last 6 months for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT53'">
        <xsl:text>Number of Required payments in last 12 months for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT55'">
        <xsl:text>Number of Missed payments in last month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT56'">
        <xsl:text>Number of Missed payments in last 3 months for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT57'">
        <xsl:text>Number of Missed payments in last 6 months for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT58'">
        <xsl:text>Number of Missed payments in last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT58'">
        <xsl:text>Number of Missed payments in last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT60'">
        <xsl:text>Missed payments ratio last month (lag required) for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT61'">
        <xsl:text>Missed payments ratio last 3 months (lag required) for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT62'">
        <xsl:text>Missed payments ratio last 6 months (lag required) for  trades</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PAYMNT63'">
        <xsl:text>Missed payments ratio last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR01'">
        <xsl:text>Revolver bankcard utilization </xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR03'">
        <xsl:text>Total revolver bankcard balance </xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR05'">
        <xsl:text>Ratio of revolver bankcard to total bankcard balance</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR07'">
        <xsl:text>Revolver bankcards</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR08'">
        <xsl:text>Revolver bankcards over past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR09'">
        <xsl:text>Revolver bankcards over past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR10'">
        <xsl:text>Number of revolver bankcards on newly opened cards</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR29'">
        <xsl:text>Bankcard balance for Bankcard 1</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR30'">
        <xsl:text>Bankcard balance for Bankcard 2</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR31'">
        <xsl:text>Bankcard balance for Bankcard 3</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR32'">
        <xsl:text>Bankcard balance for Bankcard 4</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR33'">
        <xsl:text>Bankcard balance for Bankcard 5</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV01'">
        <xsl:text>Number of months since overlimit on a bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV02'">
        <xsl:text>Number of months a bankcard overlimit in the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV03'">
        <xsl:text>Non-Mortgage Balance Decreases in last one month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV04'">
        <xsl:text>Number of non-mortgage balance increases over the past quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV05'">
        <xsl:text>Number of non-mortgage balance increase over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV06'">
        <xsl:text>Number of months with a non-mortgage balance increase over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV07'">
        <xsl:text>Number of non-mortgage balance decreases (prior month to current month)</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV08'">
        <xsl:text>Number of non-mortgage balance decreases over the past quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV09'">
        <xsl:text>Number of non-mortgage balance decreases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV10'">
        <xsl:text>Number of months with a non-mortgage balance decrease over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV11'">
        <xsl:text>Number of revolving H/C increases (prior month to current month)</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV12'">
        <xsl:text>Number of H/C increases over the past quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV13'">
        <xsl:text>Number of revolving H/C increases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV14'">
        <xsl:text>Number of months with a revolving H/C increases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV15'">
        <xsl:text>Number of credit line increases (prior month to current month)</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV16'">
        <xsl:text>Number of credit line increases over the past quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV17'">
        <xsl:text>Number of credit line increases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV18'">
        <xsl:text>Number of months with a credit line increases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV19'">
        <xsl:text>Number of credit line decreases (prior month to current month)</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV20'">
        <xsl:text>Number of credit line decreases over the past quarter</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV21'">
        <xsl:text>Number of credit line decreases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV22'">
        <xsl:text>Number of months with a credit line decreases over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRV23'">
        <xsl:text>Number of mortgage balance decreases over the last 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR01'">
        <xsl:text>Number of wallet share shifts > 25%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR02'">
        <xsl:text>Number of wallet share shifts > 25% in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR03'">
        <xsl:text>Number of wallet share shifts > 25% in past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR04'">
        <xsl:text>Number of wallet share shifts > 50%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR05'">
        <xsl:text>Number of wallet share shifts > 50% in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR06'">
        <xsl:text>Number of wallet share shifts > 50% in past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR07'">
        <xsl:text>Max wallet share shift in 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR08'">
        <xsl:text>Max wallet share shift in 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR09'">
        <xsl:text>Months since w/s shift >25% w/in 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHR10'">
        <xsl:text>Months since w/s shift >50% w/in 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV01'">
        <xsl:text>Months since most recent charge-off occurrence</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV10'">
        <xsl:text>Number of accounts 30 or more days past due ever</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV11'">
        <xsl:text>Number of accounts 60 or more days past due ever</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV12'">
        <xsl:text>Number of accounts 90 or more days past due ever</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV13'">
        <xsl:text>Percentage of accounts ever delinquent</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV17'">
        <xsl:text>Number of accounts prior 30 days past due, now current, verified in past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV18'">
        <xsl:text>Number of accounts prior 60 days past due, now current, verified in past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV19'">
        <xsl:text>Total balance of accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV20'">
        <xsl:text>Total monthly obligation of accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV21'">
        <xsl:text>Total payment amount of accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV22'">
        <xsl:text>Total balance of bankcard accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV23'">
        <xsl:text>Total monthly obligation of bankcard accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV24'">
        <xsl:text>Total payment amount of bankcard accounts verified in past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV25'">
        <xsl:text>Percent of accounts switching from inactive to active status in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV26'">
        <xsl:text>Percent of accounts switching from active to inactive status in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV27'">
        <xsl:text>Percent of bankcard accounts switching from inactive to active status in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV28'">
        <xsl:text>Percent of bankcard accounts switching from active to inactive status in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS901'">
        <xsl:text>Aggregate revolving spend over the last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS902'">
        <xsl:text>Aggregate revolving spend over the last 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS903'">
        <xsl:text>Aggregate revolving spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS904'">
        <xsl:text>Peak monthly revolving spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS905'">
        <xsl:text>Months since peak monthly revolving spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSRES01'">
        <xsl:text>spend on first revolving trade relative to total revolving spend over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSRES02'">
        <xsl:text>spend on first revolving trade relative to total revolving spend over the past year</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BCPMTSTR'">
        <xsl:text>Categorize Consumer by Bank Card Payment Behavior</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BCPMTNUM'">
        <xsl:text>Categorize Consumer by Bank Card Payment Behavior</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC11'">
        <xsl:text>Number of instances where a bankcard was utilized more than 25% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC12'">
        <xsl:text>Number of instances where a bankcard was utilized more than 50% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC13'">
        <xsl:text>Number of instances where a bankcard was utilized more than 75% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC14'">
        <xsl:text>Number of instances where a bankcard was utilized more than 90% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC51'">
        <xsl:text>Number of bankcards utilized more than 25% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC52'">
        <xsl:text>Number of bankcards utilized more than 50% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC53'">
        <xsl:text>Number of bankcards utilized more than 75% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC54'">
        <xsl:text>Number of bankcards utilized more than 90% in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC81'">
        <xsl:text>Months since a bankcard account last exceeded 25% utilization</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC82'">
        <xsl:text>Months since a bankcard account last exceeded 50% utilization</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC83'">
        <xsl:text>Months since a bankcard account last exceeded 75% utilization</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC84'">
        <xsl:text>Months since a bankcard account last exceeded 90% utilization</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC92'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized less than 25% was more than 25%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC102'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized less than 50% was more than 25%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC112'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized less than 75% was more than 25%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC122'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized less than 100% was more than 25%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC132'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized more than 25% was more than 90%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC142'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized more than 50% was more than 90%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC152'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized more than 75% was more than 90%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC162'">
        <xsl:text>Number of months in the past 12 months where percentage of bankcards utilized more than 100% was more than 90%</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS901'">
        <xsl:text>Aggregate spend over the last 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS902'">
        <xsl:text>Aggregate spend over the last 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS903'">
        <xsl:text>Aggregate spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS904'">
        <xsl:text>Peak monthly spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS905'">
        <xsl:text>Months since peak monthly spend over the last 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS906'">
        <xsl:text>Current Credit Limit of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS907'">
        <xsl:text>Annual Spend of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS908'">
        <xsl:text>Age of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS909'">
        <xsl:text>Current Balance of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS910'">
        <xsl:text>Current High Credit of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS911'">
        <xsl:text>Current Utilization of top-of-wallet bankcard</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHRS01'">
        <xsl:text>Spend on first bankcard relative to total bankcard spend over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='WALSHRS02'">
        <xsl:text>Spend on first bankcard relative to total bankcard spend over the past year</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG101'">
        <xsl:text>non-mortgage balance as of latest month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG102'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG103'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG104'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG105'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG106'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG107'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG108'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG109'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG110'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG111'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG112'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG113'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG114'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG115'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG116'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG117'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG118'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG119'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG120'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG121'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG122'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG123'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG124'">
        <xsl:text>Aggregate  non-mortgage balance at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG201'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG202'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG203'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG204'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG205'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG206'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG207'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG208'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG209'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG210'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG211'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG212'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG213'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG214'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG215'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG216'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG217'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG218'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG219'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG220'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG221'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG222'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG223'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG224'">
        <xsl:text>Aggregate  non-mortgage credit line at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG301'">
        <xsl:text>non-mortgage  amount past due as of latest month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG302'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG303'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG304'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG305'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG306'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG307'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG308'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG309'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG310'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG311'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG312'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG313'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG314'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG315'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG316'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG317'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG318'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG319'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG320'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG321'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG322'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG323'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG324'">
        <xsl:text>Aggregate  non-mortgage amount past due at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG401'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG402'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG403'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG404'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG405'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG406'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG407'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG408'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG409'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG410'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG411'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG412'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG413'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG414'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG415'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG416'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG417'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG418'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG419'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG420'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG421'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG422'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG423'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG424'">
        <xsl:text>Aggregate  non-mortgage actual payment amount at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG501'">
        <xsl:text>Aggregate bankcard balance at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG502'">
        <xsl:text>Aggregate bankcard balance at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG503'">
        <xsl:text>Aggregate bankcard balance at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG504'">
        <xsl:text>Aggregate bankcard balance at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG505'">
        <xsl:text>Aggregate bankcard balance at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG506'">
        <xsl:text>Aggregate bankcard balance at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG507'">
        <xsl:text>Aggregate bankcard balance at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG508'">
        <xsl:text>Aggregate bankcard balance at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG509'">
        <xsl:text>Aggregate bankcard balance at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG510'">
        <xsl:text>Aggregate bankcard balance at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG511'">
        <xsl:text>Aggregate bankcard balance at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG512'">
        <xsl:text>Aggregate bankcard balance at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG513'">
        <xsl:text>Aggregate bankcard balance at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG514'">
        <xsl:text>Aggregate bankcard balance at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG515'">
        <xsl:text>Aggregate bankcard balance at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG516'">
        <xsl:text>Aggregate bankcard balance at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG517'">
        <xsl:text>Aggregate bankcard balance at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG518'">
        <xsl:text>Aggregate bankcard balance at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG519'">
        <xsl:text>Aggregate bankcard balance at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG520'">
        <xsl:text>Aggregate bankcard balance at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG521'">
        <xsl:text>Aggregate bankcard balance at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG522'">
        <xsl:text>Aggregate bankcard balance at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG523'">
        <xsl:text>Aggregate bankcard balance at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG524'">
        <xsl:text>Aggregate bankcard balance at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG601'">
        <xsl:text>Aggregate bankcard credit line at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG602'">
        <xsl:text>Aggregate bankcard credit line at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG603'">
        <xsl:text>Aggregate bankcard credit line at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG604'">
        <xsl:text>Aggregate bankcard credit line at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG605'">
        <xsl:text>Aggregate bankcard credit line at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG606'">
        <xsl:text>Aggregate bankcard credit line at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG607'">
        <xsl:text>Aggregate bankcard credit line at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG608'">
        <xsl:text>Aggregate bankcard credit line at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG609'">
        <xsl:text>Aggregate bankcard credit line at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG610'">
        <xsl:text>Aggregate bankcard credit line at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG611'">
        <xsl:text>Aggregate bankcard credit line at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG612'">
        <xsl:text>Aggregate bankcard credit line at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG613'">
        <xsl:text>Aggregate bankcard credit line at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG614'">
        <xsl:text>Aggregate bankcard credit line at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG615'">
        <xsl:text>Aggregate bankcard credit line at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG616'">
        <xsl:text>Aggregate bankcard credit line at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG617'">
        <xsl:text>Aggregate bankcard credit line at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG618'">
        <xsl:text>Aggregate bankcard credit line at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG619'">
        <xsl:text>Aggregate bankcard credit line at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG620'">
        <xsl:text>Aggregate bankcard credit line at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG621'">
        <xsl:text>Aggregate bankcard credit line at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG622'">
        <xsl:text>Aggregate bankcard credit line at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG623'">
        <xsl:text>Aggregate bankcard credit line at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG624'">
        <xsl:text>Aggregate bankcard credit line at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG701'">
        <xsl:text>Aggregate bankcard amount past due at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG702'">
        <xsl:text>Aggregate bankcard amount past due at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG703'">
        <xsl:text>Aggregate bankcard amount past due at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG704'">
        <xsl:text>Aggregate bankcard amount past due at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG705'">
        <xsl:text>Aggregate bankcard amount past due at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG706'">
        <xsl:text>Aggregate bankcard amount past due at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG707'">
        <xsl:text>Aggregate bankcard amount past due at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG708'">
        <xsl:text>Aggregate bankcard amount past due at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG709'">
        <xsl:text>Aggregate bankcard amount past due at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG710'">
        <xsl:text>Aggregate bankcard amount past due at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG711'">
        <xsl:text>Aggregate bankcard amount past due at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG712'">
        <xsl:text>Aggregate bankcard amount past due at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG713'">
        <xsl:text>Aggregate bankcard amount past due at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG714'">
        <xsl:text>Aggregate bankcard amount past due at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG715'">
        <xsl:text>Aggregate bankcard amount past due at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG716'">
        <xsl:text>Aggregate bankcard amount past due at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG717'">
        <xsl:text>Aggregate bankcard amount past due at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG718'">
        <xsl:text>Aggregate bankcard amount past due at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG719'">
        <xsl:text>Aggregate bankcard amount past due at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG720'">
        <xsl:text>Aggregate bankcard amount past due at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG721'">
        <xsl:text>Aggregate bankcard amount past due at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG722'">
        <xsl:text>Aggregate bankcard amount past due at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG723'">
        <xsl:text>Aggregate bankcard amount past due at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG724'">
        <xsl:text>Aggregate bankcard amount past due at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG801'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG802'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG803'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG804'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG805'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG806'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG807'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG808'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG809'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG810'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG811'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG812'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG813'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG814'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG815'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG816'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG817'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG818'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG819'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG820'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG821'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG822'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG823'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG824'">
        <xsl:text>Aggregate bankcard actual payment amount at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1001'">
        <xsl:text>Aggregate unsecured loan balance at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1002'">
        <xsl:text>Aggregate unsecured loan balance at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1003'">
        <xsl:text>Aggregate unsecured loan balance at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1004'">
        <xsl:text>Aggregate unsecured loan balance at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1005'">
        <xsl:text>Aggregate unsecured loan balance at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1006'">
        <xsl:text>Aggregate unsecured loan balance at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1007'">
        <xsl:text>Aggregate unsecured loan balance at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1008'">
        <xsl:text>Aggregate unsecured loan balance at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1009'">
        <xsl:text>Aggregate unsecured loan balance at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1010'">
        <xsl:text>Aggregate unsecured loan balance at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1011'">
        <xsl:text>Aggregate unsecured loan balance at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1012'">
        <xsl:text>Aggregate unsecured loan balance at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1013'">
        <xsl:text>Aggregate unsecured loan balance at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1014'">
        <xsl:text>Aggregate unsecured loan balance at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1015'">
        <xsl:text>Aggregate unsecured loan balance at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1016'">
        <xsl:text>Aggregate unsecured loan balance at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1017'">
        <xsl:text>Aggregate unsecured loan balance at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1018'">
        <xsl:text>Aggregate unsecured loan balance at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1019'">
        <xsl:text>Aggregate unsecured loan balance at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1020'">
        <xsl:text>Aggregate unsecured loan balance at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1021'">
        <xsl:text>Aggregate unsecured loan balance at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1022'">
        <xsl:text>Aggregate unsecured loan balance at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1023'">
        <xsl:text>Aggregate unsecured loan balance at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1024'">
        <xsl:text>Aggregate unsecured loan balance at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1101'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1102'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1103'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1104'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1105'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1106'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1107'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1108'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1109'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1110'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1111'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1112'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1113'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1114'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1115'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1116'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1117'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1118'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1119'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1120'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1121'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1122'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1123'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1124'">
        <xsl:text>Aggregate unsecured loan credit line at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1201'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1202'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1203'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1204'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1205'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1206'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1207'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1208'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1209'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1210'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1211'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1212'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1213'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1214'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1215'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1216'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1217'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1218'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1219'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1220'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1221'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1222'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1223'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1224'">
        <xsl:text>Aggregate unsecured loan amount past due at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1301'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1302'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1303'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1304'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1305'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1306'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1307'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1308'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1309'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1310'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1311'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1312'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1313'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1314'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1315'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1316'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1317'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1318'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1319'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1320'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1321'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1322'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1323'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG1324'">
        <xsl:text>Aggregate unsecured loan actual payment amount at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR14'">
        <xsl:text>Bankcard 1 R/T/I pattern months 1 to 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR15'">
        <xsl:text>Bankcard 1 R/T/I pattern months 9 to 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR16'">
        <xsl:text>Bankcard 1 R/T/I pattern months 17 to 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR17'">
        <xsl:text>Bankcard 2 R/T/I pattern months 1 to 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR18'">
        <xsl:text>Bankcard 2 R/T/I pattern months 9 to 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR19'">
        <xsl:text>Bankcard 2 R/T/I pattern months 17 to 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR20'">
        <xsl:text>Bankcard 3 R/T/I pattern months 1 to 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR21'">
        <xsl:text>Bankcard 3 R/T/I pattern months 9 to 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR22'">
        <xsl:text>Bankcard 3 R/T/I pattern months 17 to 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR23'">
        <xsl:text>Bankcard 4 R/T/I pattern months 1 to 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR24'">
        <xsl:text>Bankcard 4 R/T/I pattern months 9 to 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR25'">
        <xsl:text>Bankcard 4 R/T/I pattern months 17 to 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR26'">
        <xsl:text>Bankcard 5 R/T/I pattern months 1 to 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR27'">
        <xsl:text>Bankcard 5 R/T/I pattern months 9 to 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RVLR28'">
        <xsl:text>Bankcard 5 R/T/I pattern months 17 to 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS101'">
        <xsl:text>Aggregate spend at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS102'">
        <xsl:text>Aggregate spend at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS103'">
        <xsl:text>Aggregate spend at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS104'">
        <xsl:text>Aggregate spend at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS105'">
        <xsl:text>Aggregate spend at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS106'">
        <xsl:text>Aggregate spend at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS107'">
        <xsl:text>Aggregate spend at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS108'">
        <xsl:text>Aggregate spend at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS109'">
        <xsl:text>Aggregate spend at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS110'">
        <xsl:text>Aggregate spend at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS111'">
        <xsl:text>Aggregate spend at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS112'">
        <xsl:text>Aggregate spend at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS113'">
        <xsl:text>Aggregate spend at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS114'">
        <xsl:text>Aggregate spend at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS115'">
        <xsl:text>Aggregate spend at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS116'">
        <xsl:text>Aggregate spend at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS117'">
        <xsl:text>Aggregate spend at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS118'">
        <xsl:text>Aggregate spend at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS119'">
        <xsl:text>Aggregate spend at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS120'">
        <xsl:text>Aggregate spend at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS121'">
        <xsl:text>Aggregate spend at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS122'">
        <xsl:text>Aggregate spend at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS123'">
        <xsl:text>Aggregate spend at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGGS124'">
        <xsl:text>Aggregate spend at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS101'">
        <xsl:text>Aggregate revolving spend at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS102'">
        <xsl:text>Aggregate revolving spend at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS103'">
        <xsl:text>Aggregate revolving spend at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS104'">
        <xsl:text>Aggregate revolving spend at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS105'">
        <xsl:text>Aggregate revolving spend at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS106'">
        <xsl:text>Aggregate revolving spend at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS107'">
        <xsl:text>Aggregate revolving spend at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS108'">
        <xsl:text>Aggregate revolving spend at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS109'">
        <xsl:text>Aggregate revolving spend at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS110'">
        <xsl:text>Aggregate revolving spend at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS111'">
        <xsl:text>Aggregate revolving spend at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS112'">
        <xsl:text>Aggregate revolving spend at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS113'">
        <xsl:text>Aggregate revolving spend at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS114'">
        <xsl:text>Aggregate revolving spend at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS115'">
        <xsl:text>Aggregate revolving spend at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS116'">
        <xsl:text>Aggregate revolving spend at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS117'">
        <xsl:text>Aggregate revolving spend at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS118'">
        <xsl:text>Aggregate revolving spend at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS119'">
        <xsl:text>Aggregate revolving spend at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS120'">
        <xsl:text>Aggregate revolving spend at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS121'">
        <xsl:text>Aggregate revolving spend at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS122'">
        <xsl:text>Aggregate revolving spend at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS123'">
        <xsl:text>Aggregate revolving spend at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVS124'">
        <xsl:text>Aggregate revolving spend at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL01'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 1</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL02'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 2</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL03'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 3</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL04'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 4</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL05'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 5</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL06'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 6</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL07'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 7</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL08'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL09'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 9</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL10'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL11'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL12'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL13'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL14'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL15'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL16'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL17'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL18'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL19'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL20'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL21'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL22'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL23'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REVBAL24'">
        <xsl:text>Balance assigned to accounts identified as revolving at month 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL01'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 1</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL02'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 2</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL03'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 3</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL04'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 4</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL05'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 5</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL06'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 6</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL07'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 7</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL08'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 8</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL09'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 9</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL10'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL11'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL12'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL13'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL14'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL15'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL16'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL17'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL18'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL19'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL20'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL21'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL22'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL23'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TRANBAL24'">
        <xsl:text>Balance assigned to accounts identified as transacting at month 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9101'">
        <xsl:text>Aggregate balance at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9102'">
        <xsl:text>Aggregate balance at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9103'">
        <xsl:text>Aggregate balance at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9104'">
        <xsl:text>Aggregate balance at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9105'">
        <xsl:text>Aggregate balance at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9106'">
        <xsl:text>Aggregate balance at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9107'">
        <xsl:text>Aggregate balance at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9108'">
        <xsl:text>Aggregate balance at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9109'">
        <xsl:text>Aggregate balance at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9110'">
        <xsl:text>Aggregate balance at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9111'">
        <xsl:text>Aggregate balance at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9112'">
        <xsl:text>Aggregate balance at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9113'">
        <xsl:text>Aggregate balance at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9114'">
        <xsl:text>Aggregate balance at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9115'">
        <xsl:text>Aggregate balance at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9116'">
        <xsl:text>Aggregate balance at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9117'">
        <xsl:text>Aggregate balance at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9118'">
        <xsl:text>Aggregate balance at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9119'">
        <xsl:text>Aggregate balance at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9120'">
        <xsl:text>Aggregate balance at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9121'">
        <xsl:text>Aggregate balance at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9122'">
        <xsl:text>Aggregate balance at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9123'">
        <xsl:text>Aggregate balance at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9124'">
        <xsl:text>Aggregate balance at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9201'">
        <xsl:text>Aggregate  credit line at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9202'">
        <xsl:text>Aggregate  credit line at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9203'">
        <xsl:text>Aggregate  credit line at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9204'">
        <xsl:text>Aggregate  credit line at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9205'">
        <xsl:text>Aggregate  credit line at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9206'">
        <xsl:text>Aggregate  credit line at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9207'">
        <xsl:text>Aggregate  credit line at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9208'">
        <xsl:text>Aggregate  credit line at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9209'">
        <xsl:text>Aggregate  credit line at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9210'">
        <xsl:text>Aggregate  credit line at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9211'">
        <xsl:text>Aggregate  credit line at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9212'">
        <xsl:text>Aggregate  credit line at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9213'">
        <xsl:text>Aggregate  credit line at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9214'">
        <xsl:text>Aggregate  credit line at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9215'">
        <xsl:text>Aggregate  credit line at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9216'">
        <xsl:text>Aggregate  credit line at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9217'">
        <xsl:text>Aggregate  credit line at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9218'">
        <xsl:text>Aggregate  credit line at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9219'">
        <xsl:text>Aggregate  credit line at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9220'">
        <xsl:text>Aggregate  credit line at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9221'">
        <xsl:text>Aggregate  credit line at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9222'">
        <xsl:text>Aggregate  credit line at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9223'">
        <xsl:text>Aggregate  credit line at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9224'">
        <xsl:text>Aggregate  credit line at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9301'">
        <xsl:text>Aggregate  amount past due at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9302'">
        <xsl:text>Aggregate  amount past due at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9303'">
        <xsl:text>Aggregate  amount past due at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9304'">
        <xsl:text>Aggregate  amount past due at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9305'">
        <xsl:text>Aggregate  amount past due at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9306'">
        <xsl:text>Aggregate  amount past due at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9307'">
        <xsl:text>Aggregate  amount past due at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9308'">
        <xsl:text>Aggregate  amount past due at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9309'">
        <xsl:text>Aggregate  amount past due at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9310'">
        <xsl:text>Aggregate  amount past due at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9311'">
        <xsl:text>Aggregate  amount past due at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9312'">
        <xsl:text>Aggregate  amount past due at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9313'">
        <xsl:text>Aggregate  amount past due at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9314'">
        <xsl:text>Aggregate  amount past due at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9315'">
        <xsl:text>Aggregate  amount past due at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9316'">
        <xsl:text>Aggregate  amount past due at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9317'">
        <xsl:text>Aggregate  amount past due at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9318'">
        <xsl:text>Aggregate  amount past due at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9319'">
        <xsl:text>Aggregate  amount past due at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9320'">
        <xsl:text>Aggregate  amount past due at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9321'">
        <xsl:text>Aggregate  amount past due at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9322'">
        <xsl:text>Aggregate  amount past due at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9323'">
        <xsl:text>Aggregate  amount past due at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9324'">
        <xsl:text>Aggregate  amount past due at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9401'">
        <xsl:text>Aggregate  actual payment amount at month M = 01</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9402'">
        <xsl:text>Aggregate  actual payment amount at month M = 02</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9403'">
        <xsl:text>Aggregate  actual payment amount at month M = 03</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9404'">
        <xsl:text>Aggregate  actual payment amount at month M = 04</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9405'">
        <xsl:text>Aggregate  actual payment amount at month M = 05</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9406'">
        <xsl:text>Aggregate  actual payment amount at month M = 06</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9407'">
        <xsl:text>Aggregate  actual payment amount at month M = 07</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9408'">
        <xsl:text>Aggregate  actual payment amount at month M = 08</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9409'">
        <xsl:text>Aggregate  actual payment amount at month M = 09</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9410'">
        <xsl:text>Aggregate  actual payment amount at month M = 10</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9411'">
        <xsl:text>Aggregate  actual payment amount at month M = 11</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9412'">
        <xsl:text>Aggregate  actual payment amount at month M = 12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9413'">
        <xsl:text>Aggregate  actual payment amount at month M = 13</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9414'">
        <xsl:text>Aggregate  actual payment amount at month M = 14</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9415'">
        <xsl:text>Aggregate  actual payment amount at month M = 15</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9416'">
        <xsl:text>Aggregate  actual payment amount at month M = 16</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9417'">
        <xsl:text>Aggregate  actual payment amount at month M = 17</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9418'">
        <xsl:text>Aggregate  actual payment amount at month M = 18</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9419'">
        <xsl:text>Aggregate  actual payment amount at month M = 19</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9420'">
        <xsl:text>Aggregate  actual payment amount at month M = 20</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9421'">
        <xsl:text>Aggregate  actual payment amount at month M = 21</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9422'">
        <xsl:text>Aggregate  actual payment amount at month M = 22</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9423'">
        <xsl:text>Aggregate  actual payment amount at month M = 23</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AGG9424'">
        <xsl:text>Aggregate  actual payment amount at month M = 24</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC201'">
        <xsl:text>Total payment ratio for bankcard accounts over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC202'">
        <xsl:text>Total payment ratio for bankcard accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC203'">
        <xsl:text>Total payment ratio for bankcard accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC204'">
        <xsl:text>Total payment ratio for bankcard accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC205'">
        <xsl:text>Total payment ratio for bankcard accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC222'">
        <xsl:text>Average payment ratio for bankcard accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC223'">
        <xsl:text>Average payment ratio for bankcard accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC224'">
        <xsl:text>Average payment ratio for bankcard accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC225'">
        <xsl:text>Average payment ratio for bankcard accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT201'">
        <xsl:text>Total payment ratio for auto loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT202'">
        <xsl:text>Total payment ratio for auto loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT203'">
        <xsl:text>Total payment ratio for auto loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT204'">
        <xsl:text>Total payment ratio for auto loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT205'">
        <xsl:text>Total payment ratio for auto loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT222'">
        <xsl:text>Average payment ratio for auto loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT223'">
        <xsl:text>Average payment ratio for auto loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT224'">
        <xsl:text>Average payment ratio for auto loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT225'">
        <xsl:text>Average payment ratio for auto loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD201'">
        <xsl:text>Total payment ratio for student loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD202'">
        <xsl:text>Total payment ratio for student loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD203'">
        <xsl:text>Total payment ratio for student loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD204'">
        <xsl:text>Total payment ratio for student loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD205'">
        <xsl:text>Total payment ratio for student loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD222'">
        <xsl:text>Average payment ratio for student loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD223'">
        <xsl:text>Average payment ratio for student loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD224'">
        <xsl:text>Average payment ratio for student loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD225'">
        <xsl:text>Average payment ratio for student loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER201'">
        <xsl:text>Total payment ratio for personal loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER202'">
        <xsl:text>Total payment ratio for personal loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER203'">
        <xsl:text>Total payment ratio for personal loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER204'">
        <xsl:text>Total payment ratio for personal loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER205'">
        <xsl:text>Total payment ratio for personal loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER222'">
        <xsl:text>Average payment ratio for personal loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER223'">
        <xsl:text>Average payment ratio for personal loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER224'">
        <xsl:text>Average payment ratio for personal loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER225'">
        <xsl:text>Average payment ratio for personal loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO201'">
        <xsl:text>Total payment ratio for two wheeler loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO202'">
        <xsl:text>Total payment ratio for two wheeler loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO203'">
        <xsl:text>Total payment ratio for two wheeler loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO204'">
        <xsl:text>Total payment ratio for two wheeler loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO205'">
        <xsl:text>Total payment ratio for two wheeler loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO222'">
        <xsl:text>Average payment ratio for two wheeler loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO223'">
        <xsl:text>Average payment ratio for two wheeler loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO224'">
        <xsl:text>Average payment ratio for two wheeler loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO225'">
        <xsl:text>Average payment ratio for two wheeler loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL201'">
        <xsl:text>Total payment ratio for business installment loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL202'">
        <xsl:text>Total payment ratio for business installment loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL203'">
        <xsl:text>Total payment ratio for business installment loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL204'">
        <xsl:text>Total payment ratio for business installment loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL205'">
        <xsl:text>Total payment ratio for business installment loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL222'">
        <xsl:text>Average payment ratio for business installment loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL223'">
        <xsl:text>Average payment ratio for business installment loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL224'">
        <xsl:text>Average payment ratio for business installment loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL225'">
        <xsl:text>Average payment ratio for business installment loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV201'">
        <xsl:text>Total payment ratio for commercial vehicle loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV202'">
        <xsl:text>Total payment ratio for commercial vehicle loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV203'">
        <xsl:text>Total payment ratio for commercial vehicle loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV204'">
        <xsl:text>Total payment ratio for commercial vehicle loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV205'">
        <xsl:text>Total payment ratio for commercial vehicle loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV222'">
        <xsl:text>Average payment ratio for commercial vehicle loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV223'">
        <xsl:text>Average payment ratio for commercial vehicle loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV224'">
        <xsl:text>Average payment ratio for commercial vehicle loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV225'">
        <xsl:text>Average payment ratio for commercial vehicle loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL231'">
        <xsl:text>Aggregate excess payment for all accounts over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL232'">
        <xsl:text>Aggregate excess payment for all accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL233'">
        <xsl:text>Aggregate excess payment for all accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL234'">
        <xsl:text>Aggregate excess payment for all accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL235'">
        <xsl:text>Aggregate excess payment for all accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL252'">
        <xsl:text>Average aggregate excess payment for all accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL253'">
        <xsl:text>Average aggregate excess payment for all accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL254'">
        <xsl:text>Average aggregate excess payment for all accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='ALL255'">
        <xsl:text>Average aggregate excess payment for all accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC231'">
        <xsl:text>Aggregate excess payment for bankcard accounts over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC232'">
        <xsl:text>Aggregate excess payment for bankcard accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC233'">
        <xsl:text>Aggregate excess payment for bankcard accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC234'">
        <xsl:text>Aggregate excess payment for bankcard accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC235'">
        <xsl:text>Aggregate excess payment for bankcard accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC252'">
        <xsl:text>Average aggregate excess payment for bankcard accounts over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC253'">
        <xsl:text>Average aggregate excess payment for bankcard accounts over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC254'">
        <xsl:text>Average aggregate excess payment for bankcard accounts over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BKC255'">
        <xsl:text>Average aggregate excess payment for bankcard accounts over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT231'">
        <xsl:text>Aaggregate excess payment for auto loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT232'">
        <xsl:text>Aggregate excess payment for auto loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT233'">
        <xsl:text>Aggregate excess payment for auto loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT234'">
        <xsl:text>Aggregate excess payment for auto loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT235'">
        <xsl:text>Aggregate excess payment for auto loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT252'">
        <xsl:text>Average aggregate excess payment for auto loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT253'">
        <xsl:text>Average aggregate excess payment for auto loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT254'">
        <xsl:text>Average aggregate excess payment for auto loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AUT255'">
        <xsl:text>Average aggregate excess payment for auto loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD231'">
        <xsl:text>Aggregate excess payment for student loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD232'">
        <xsl:text>Aggregate excess payment for student loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD233'">
        <xsl:text>Aggregate excess payment for student loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD234'">
        <xsl:text>Aggregate excess payment for student loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD235'">
        <xsl:text>Aggregate excess payment for student loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD252'">
        <xsl:text>Average aggregate excess payment for student loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD253'">
        <xsl:text>Average aggregate excess payment for student loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD254'">
        <xsl:text>Average aggregate excess payment for student loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='STD255'">
        <xsl:text>Average aggregate excess payment for student loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER231'">
        <xsl:text>Aggregate excess payment for personal loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER232'">
        <xsl:text>Aggregate excess payment for personal loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER233'">
        <xsl:text>Aggregate excess payment for personal loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER234'">
        <xsl:text>Aggregate excess payment for personal loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER235'">
        <xsl:text>Aggregate excess payment for personal loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER252'">
        <xsl:text>Average aggregate excess payment for personal loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER253'">
        <xsl:text>Average aggregate excess payment for personal loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER254'">
        <xsl:text>Average aggregate excess payment for personal loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='PER255'">
        <xsl:text>Average aggregate excess payment for personal loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO231'">
        <xsl:text>Aggregate excess payment for two wheeler loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO232'">
        <xsl:text>Aggregate excess payment for two wheeler loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO233'">
        <xsl:text>Aggregate excess payment for two wheeler loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO234'">
        <xsl:text>Aggregate excess payment for two wheeler loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO235'">
        <xsl:text>Aggregate excess payment for two wheeler loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO252'">
        <xsl:text>Average aggregate excess payment for two wheeler loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO253'">
        <xsl:text>Average aggregate excess payment for two wheeler loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO254'">
        <xsl:text>Average aggregate excess payment for two wheeler loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='TWO255'">
        <xsl:text>Average aggregate excess payment for two wheeler loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL231'">
        <xsl:text>Aggregate excess payment for business installment loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL232'">
        <xsl:text>Aggregate excess payment for business installment loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL233'">
        <xsl:text>Aggregate excess payment for business installment loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL234'">
        <xsl:text>Aggregate excess payment for business installment loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL235'">
        <xsl:text>Aggregate excess payment for business installment loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL252'">
        <xsl:text>Average aggregate excess payment for business installment loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL253'">
        <xsl:text>Average aggregate excess payment for business installment loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL254'">
        <xsl:text>Average aggregate excess payment for business installment loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='BIL255'">
        <xsl:text>Average aggregate excess payment for business installment loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV231'">
        <xsl:text>Aggregate excess payment for commercial vehicle loans over the past month</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV232'">
        <xsl:text>Aggregate excess payment for commercial vehicle loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV233'">
        <xsl:text>Aggregate excess payment for commercial vehicle loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV234'">
        <xsl:text>Aggregate excess payment for commercial vehicle loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV235'">
        <xsl:text>Aggregate excess payment for commercial vehicle loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV252'">
        <xsl:text>Average aggregate excess payment for commercial vehicle loans over the past 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV253'">
        <xsl:text>Average aggregate excess payment for commercial vehicle loans over the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV254'">
        <xsl:text>Average aggregate excess payment for commercial vehicle loans over the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CMV255'">
        <xsl:text>Average aggregate excess payment for commercial vehicle loans over the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='REV315'">
        <xsl:text>Number of months since max total open-to-buy for revolving accounts</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE901'">
        <xsl:text>Number of over-payments on real estate accounts in the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE902'">
        <xsl:text>Number of over-payments on real estate accounts in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE903'">
        <xsl:text>Number of over-payments on real estate accounts in the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE904'">
        <xsl:text>Amount of over-payments on real estate accounts in the past 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE905'">
        <xsl:text>Amount of over-payments on real estate accounts in the past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE906'">
        <xsl:text>Amount of over-payments on real estate accounts in the past 24 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='RLE907'">
        <xsl:text>Months since most recent over-payment on a real estate account</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='CV14'">
        <xsl:text>TotalNoOfEnquiries</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AT29S'">
        <xsl:text>TotalNoOfZeroBalanceAccounts</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AT33A'">
        <xsl:text>TotalCurrentBalance</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AT57S'">
        <xsl:text>Tot_OverdueAmt</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AT28A'">
        <xsl:text>Tot_HighCrdAmt_Acc_Opened_Last12</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='G001B'">
        <xsl:text>Number of 30 or more days past due in past 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='AT21S'">
        <xsl:text>Months since most recent trade opened</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='G103S'">
        <xsl:text>Months since most recent credit inquiry</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM201S'">
        <xsl:text>Numer of phones first reported in 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM202S'">
        <xsl:text>Numer of phones first reported in 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM203S'">
        <xsl:text>Numer of phones first reported in 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM206S'">
        <xsl:text>Months since last update of phone</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM211S'">
        <xsl:text>Numer of addresses first reported in 3 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM212S'">
        <xsl:text>Numer of addresses first reported in 6 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM213S'">
        <xsl:text>Numer of addresses first reported in 12 months</xsl:text>
    </xsl:if>
    <xsl:if test="$cvId ='DM216S'">
        <xsl:text>Months since last update of address</xsl:text>
    </xsl:if>
</xsl:template>

<!-- Template For CV DESCRIPTION (bureau Characteristics) Ended  -->



<!-- Template To Upper case -->
<xsl:template name="ToUpper">
    <xsl:param name="data"/>
    <xsl:value-of select="translate($data,'abcdefghijklmnopqrstuvwxyz' , 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
</xsl:template>
<!-- Template To Upper case Ended -->


<xsl:template name="get_PossibleRange">
    <xsl:param name="rangeId"/>
    <xsl:if test="$rangeId=''">
        <xsl:text>Refer TUEF Guide</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='PAYMNT55'">
        <xsl:text>0 to More than 1</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='PAYMNT58'">
        <xsl:text>Less than 1 to More than 3</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='PAYMNT63'">
        <xsl:text>Less than 2 to More than 6 (%)</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='CV10'">
        <xsl:text>Less than 2 to More than 6</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='CV11'">
        <xsl:text>Less than 2 to More than 6</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='CV12'">
        <xsl:text>Less than 1 to More than 4</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='CV13'">
        <xsl:text>Less than 4 to More than 10 (%)</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='BALMAG01'">
        <xsl:text>Less than 180 to More than 250</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AGG901'">
        <xsl:text>More than 3 to Less than 2</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AGG902'">
        <xsl:text>Less Than 1 to More Than 3</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='TRV03'">
        <xsl:text>Less Than 1 to More Than 2</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='CV14'">
        <xsl:text>Less Than 6 to More than 12</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AT21S'">
        <xsl:text>Less Than 6 to More than 12</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='G103S'">
        <xsl:text>Less Than 3 to More than 12</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AGG101'">
        <xsl:text>Less than INR 60,000 to More than INR 1,50,000</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AGG301'">
        <xsl:text>No Overdue to More than INR 5,000</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AT57S'">
        <xsl:text>No Overdue to More than INR 5,000</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='G001B'">
        <xsl:text>Less than 2 to More than 6</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AT29S'">
        <xsl:text>Summary View</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AT33A'">
        <xsl:text>Summary View</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='AT28A'">
        <xsl:text>Summary View</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='TRD'">
        <xsl:text>Summary View</xsl:text>
    </xsl:if>
    <xsl:if test="$rangeId ='DM201S'">
        <xsl:value-of select="'&amp;le;1 Low Risk, 2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM202S'">
        <xsl:value-of select="'&amp;le;1 Low Risk, 2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM203S'">
        <xsl:value-of select="'&amp;le;1 Low Risk, 2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM206S'">
        <xsl:value-of select="'&amp;lt;0 Low Risk, &amp;le;3 High Risk, &amp;le;6 Medium Risk, &amp;gt;6 Low Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM216S'">
        <xsl:value-of select="'&amp;lt;0 Low Risk, &amp;le;3 High Risk, &amp;le;6 Medium Risk, &amp;gt;6 Low Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM211S'">
        <xsl:value-of select="'=1 Low Risk, =2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM212S'">
        <xsl:value-of select="'=1 Low Risk, =2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
    <xsl:if test="$rangeId ='DM213S'">
        <xsl:value-of select="'=1 Low Risk, =2 Medium Risk, &amp;ge;3 High Risk'"/>
    </xsl:if>
</xsl:template>



<!-- Template PAYMENT Behavior  -->
<xsl:template name="get_paybe">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='PAYMNT55' or $data='PAYMNT58' or $data='PAYMNT55' or $data='CV10' or $data='CV11' or $data='CV12' or $data='CV13'">
            <xsl:text>true</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>false</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template PAYMENT Behavior end   -->


<!-- Template Leverage Behaviour -->
<xsl:template name="get_levbe">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='BALMAG01' or $data='AGG901' or $data='AGG902' or $data='TRV03'">
            <xsl:text>true</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>false</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template Leverage Behaviour End -->

<!-- Template Credit Activity &amp; Vintage of Credit Activity -->

<xsl:template name="get_credit">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='CV14' or $data='AT21S' or $data='G103S'">
            <xsl:text>true</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>false</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template Credit Activity &amp; Vintage of Credit Activity End -->

<!-- Template Credit Snapshot  -->
<xsl:template name="get_credit_snap">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='AGG101' or $data='AGG301' or $data='AT57S' or $data='G001B'  or $data='AT29S' or $data='AT33A' or $data='AT28A' or $data='TRD'">
            <xsl:text>true</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>false</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template Credit Snapshot End -->

<!-- Template Demographic Stability -->
<xsl:template name="get_Demographic_Stability">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='DM202S' or $data='DM212S' or $data='DM216S' or $data='DM206S' or $data='DM211S' or $data='DM213S' or $data='DM203S' or $data='DM201S'">
            <xsl:text>true</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>false</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template CrDemographic Stability End -->

<!-- Template Others -->
<xsl:template name="hide_NTCvar">
    <xsl:param name="data"/>
    <xsl:choose>
        <xsl:when test="$data='N_DM001S' or $data='N_DM201S' or $data='N_DM202S' or $data='N_DM212S' or $data='N_DM216S' or $data='N_G106S' or $data='N_G232S' or $data='N_G242F' or $data='N_G406S' or $data='N_G412S' or $data='N_G503S' or $data='N_G518S' or $data='N_DM203S' or $data='N_G507S' or $data='N_G409S' or $data='N_G960S' or $data='N_G500S' or $data='N_DM206S' or $data='N_DM211S' or $data='N_DM004S'">
            <xsl:text>false</xsl:text>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text>true</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
<!-- Template Others End -->



<xsl:template name="getRemarkCodeDesc">
    <xsl:param name="id"/>
    <xsl:if test="$id ='PN0001'">
        <xsl:text>Certain information under Personal / Contract / Enquiry information section has been disputed by the consumer.</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PN1001'">
        <xsl:text>Consumer Name in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PN1007'">
        <xsl:text>Date of Birth in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PN1008'">
        <xsl:text>Gender in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PN1999'">
        <xsl:text>Multiple Disputes in Name (PN) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ID1001'">
        <xsl:text>ID Type in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ID1002'">
        <xsl:text>ID Number in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ID1003'">
        <xsl:text>Issue Date in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ID1004'">
        <xsl:text>Expiration Date in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ID1999'">
        <xsl:text>Multiple Disputes in Identification (ID) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PT1001'">
        <xsl:text>Telephone Number in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PT1002'">
        <xsl:text>Telephone Extension in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PT1003'">
        <xsl:text>Telephone Type in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PT1999'">
        <xsl:text>Multiple Disputes in Telephone (PT) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EC1001'">
        <xsl:text>E-Mail ID in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EC1999'">
        <xsl:text>Multiple Disputes in Email Contact (EC) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM0001'">
        <xsl:text>Certain information under Employment information section has been disputed by the consumer.</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM1003'">
        <xsl:text>Occupation Code in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM1004'">
        <xsl:text>Income in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM1005'">
        <xsl:text>Net/Gross Income Indicator in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM1006'">
        <xsl:text>Monthly/Annual Income Indicator in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='EM1999'">
        <xsl:text>Multiple Disputes in Employment (EM) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1001'">
        <xsl:text>Address Line (except State Code and PIN Code) in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1006'">
        <xsl:text>State in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1007'">
        <xsl:text>PIN Code in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1008'">
        <xsl:text>Address Category in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1009'">
        <xsl:text>Residence Code in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='PA1999'">
        <xsl:text>Multiple Disputes in Address (PA) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL0001'">
        <xsl:text>Certain information for this account has been disputed by the consumer.</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1003'">
        <xsl:text>Account Number in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1004'">
        <xsl:text>Account Type in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1005'">
        <xsl:text>NO DISPUTES</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1008'">
        <xsl:text>Ownership Indicator in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1009'">
        <xsl:text>Date of Last Payment in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1010'">
        <xsl:text>Date Closed in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1011'">
        <xsl:text>Date Reported and Certified in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1012'">
        <xsl:text>High Credit/Sanctioned Amount in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1013'">
        <xsl:text>Current Balance in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1014'">
        <xsl:text>Amount Overdue in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1030'">
        <xsl:text>Payment History Start Date in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1031'">
        <xsl:text>Payment History End Date in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1032'">
        <xsl:text>Suit Filed / Wilful Default in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1033'">
        <xsl:text>Written-off and Settled Status in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1034'">
        <xsl:text>Value of Collateral in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1035'">
        <xsl:text>Type of Collateral in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1036'">
        <xsl:text>Credit Limit in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1037'">
        <xsl:text>Cash Limit in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1038'">
        <xsl:text>Rate Of Interest in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1039'">
        <xsl:text>Repayment Tenure in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1040'">
        <xsl:text>EMI Amount in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1041'">
        <xsl:text>Written-off Amount (Total) in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1042'">
        <xsl:text>Written-off Amount (Principal) in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1043'">
        <xsl:text>Settlement Amount in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1044'">
        <xsl:text>Payment Frequency in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1045'">
        <xsl:text>Actual Payment Amount in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1101'">
        <xsl:text>Payment History 1 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1102'">
        <xsl:text>Payment History 2 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1103'">
        <xsl:text>Payment History 3 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1104'">
        <xsl:text>Payment History 4 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1105'">
        <xsl:text>Payment History 5 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1106'">
        <xsl:text>Payment History 6 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1107'">
        <xsl:text>Payment History 7 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1108'">
        <xsl:text>Payment History 8 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1109'">
        <xsl:text>Payment History 9 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1110'">
        <xsl:text>Payment History 10 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1111'">
        <xsl:text>Payment History 11 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1112'">
        <xsl:text>Payment History 12 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1113'">
        <xsl:text>Payment History 13 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1114'">
        <xsl:text>Payment History 14 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1115'">
        <xsl:text>Payment History 15 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1116'">
        <xsl:text>Payment History 16 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1117'">
        <xsl:text>Payment History 17 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1118'">
        <xsl:text>Payment History 18 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1119'">
        <xsl:text>Payment History 19 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1120'">
        <xsl:text>Payment History 20 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1121'">
        <xsl:text>Payment History 21 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1122'">
        <xsl:text>Payment History 22 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1123'">
        <xsl:text>Payment History 23 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1124'">
        <xsl:text>Payment History 24 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1125'">
        <xsl:text>Payment History 25 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1126'">
        <xsl:text>Payment History 26 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1127'">
        <xsl:text>Payment History 27 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1128'">
        <xsl:text>Payment History 28 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1129'">
        <xsl:text>Payment History 29 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1130'">
        <xsl:text>Payment History 30 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1131'">
        <xsl:text>Payment History 31 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1132'">
        <xsl:text>Payment History 32 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1133'">
        <xsl:text>Payment History 33 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1134'">
        <xsl:text>Payment History 34 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1135'">
        <xsl:text>Payment History 35 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1136'">
        <xsl:text>Payment History 36 in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1886'">
        <xsl:text>Duplicate Account</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1888'">
        <xsl:text>Account Ownership Error</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='TL1999'">
        <xsl:text>Multiple Disputes in Account (TL) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='IQ1001'">
        <xsl:text>Enquiry Purpose in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='IQ1006'">
        <xsl:text>Enquiry Amount in Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='IQ1888'">
        <xsl:text>Enquiry Ownership Error</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='IQ1999'">
        <xsl:text>Multiple Disputes in Enquiry (IQ) Segment</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='000001'">
        <xsl:text>One or more Members have not responded to your Dispute</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='000002'">
        <xsl:text>Dispute accepted – pending correction by the Member</xsl:text>
    </xsl:if>
    <xsl:if test="$id ='ZZ0999'">
        <xsl:text>Multiple Disputes in multiple segments</xsl:text>
    </xsl:if>
    <xsl:if test="$id=''">
        <xsl:text></xsl:text>
    </xsl:if>
</xsl:template>


<xsl:template name="getDisputeRemarkCodeDesc">
    <xsl:param name="id"/>
    <xsl:if test="$id=''">
        <xsl:text></xsl:text>
    </xsl:if>
    <xsl:if test="$id='000001'">
        <xsl:text>Disputed accepted – under investigation.</xsl:text>
    </xsl:if>
</xsl:template>


<!-- Error Message Template -->
<xsl:template name="GetErrorSegmentDescription">
    <xsl:param name="errroSegment"/>
    <xsl:if test="$errroSegment ='PNN0101'">
        <xsl:text>Provided Consumer Name Field 1 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0102'">
        <xsl:text>Provided Consumer Name Field 2 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0103'">
        <xsl:text>Provided Consumer Name Field 3 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0104'">
        <xsl:text>Provided Consumer Name Field 4 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0105'">
        <xsl:text>Provided Consumer Name Field 5 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0107'">
        <xsl:text>Provided DOB is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PNN0108'">
        <xsl:text>Provided Gender is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='ID/PT'">
        <xsl:text>Either Identifier or Telephone is mandatory.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI01'">
        <xsl:text>Provided Identifier Segment - 01 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI02'">
        <xsl:text>Provided Identifier Segment - 02 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI03'">
        <xsl:text>-Provided Identifier Segment - 03 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI04'">
        <xsl:text>Provided Identifier Segment - 04 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI05'">
        <xsl:text>Provided Identifier Segment - 05 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI06'">
        <xsl:text>Requested Response Size Exceeded.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI07'">
        <xsl:text>Provided Identifier Segment - 07 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='IDI08'">
        <xsl:text>Provided Identifier Segment - 08 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PTT01'">
        <xsl:text>Provided Telephone Segment -01 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PTT02'">
        <xsl:text>Provided Telephone Segment - 02 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PTT03'">
        <xsl:text>Provided Telephone Segment - 03 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PTT04'">
        <xsl:text>Provided Telephone Segment - 04 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PAA01'">
        <xsl:text>Provided Address Segment - 01 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PAA02'">
        <xsl:text>Provided Address Segment - 02 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PAA03'">
        <xsl:text>Provided Address Segment - 03 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PAA04'">
        <xsl:text>Provided Address Segment - 04 is invalid.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PA'">
        <xsl:text>Address Segment is missing.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment ='PI'">
        <xsl:text>Invalid Account Segment.</xsl:text>
    </xsl:if>
    <xsl:if test="$errroSegment = ''">
        <xsl:text>message</xsl:text>
    </xsl:if>
</xsl:template>
<!-- Error Message Template Ended -->


<xsl:template name="ErrorMessage">
    <xsl:param name="ErrMsg"/>
    <xsl:variable name="baseMessage">
        <xsl:value-of select="'YOUR REQUEST HAS BEEN REJECTED BY THE CREDIT BUREAU SERVER.PLEASE MAKE THE APPROPRIATE CHANGE AND RESUBMIT THE REQUEST OR CONTACT THE SYSTEM ADMINISTRATOR.'"/>
    </xsl:variable>
    <xsl:variable name="message">
        <xsl:call-template name="extractErrorMessage">
            <xsl:with-param name="errorString" select="$ErrMsg"/>
        </xsl:call-template>
    </xsl:variable>
    <!--  <xsl:if test="contains($message,':')"><xsl:call-template name="colonMessage"><xsl:with-param name="errorMessage" select="$message"/>
	 		</xsl:call-template>
	 	</xsl:if> -->
<p>
    <xsl:value-of select="concat($baseMessage, ':',$message,' ')"/>
</p>
</xsl:template>
<xsl:template name="extractErrorMessage">
    <xsl:param name="errorString"/>
    <xsl:variable name="processedMessage">
        <xsl:if test="string-length(normalize-space($errorString))  &gt; 0 and contains($errorString,';')">
            <xsl:call-template name="semiColonMessage">
                <xsl:with-param name="message" select="$errorString"/>
                <xsl:with-param name="preparedString" select="''"/>
            </xsl:call-template>
        </xsl:if>
        <xsl:if test="string-length(normalize-space($errorString))  &gt; 0 and contains($errorString,':')">
            <xsl:call-template name="colonMessage">
                <xsl:with-param name="errorMessage" select="$errorString"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:variable>
    <xsl:value-of select="$processedMessage"/>
</xsl:template>
<xsl:template name="semiColonMessage">
    <xsl:param name="message"/>
    <xsl:param name="preparedString"/>
    <xsl:variable name="innerText" select="substring-after($message,';')"/>
    <xsl:variable name="errMessage">
        <xsl:if test="contains($innerText,'Message')">
            <xsl:value-of select="normalize-space(translate(translate($innerText,'Message',''),':',''))"/>
        </xsl:if>
    </xsl:variable>
    <xsl:variable name="valueMessage">
        <xsl:if test="contains($innerText,'Value')">
            <xsl:call-template name="GetErrorSegmentDescription">
                <xsl:with-param name="errroSegment" select="normalize-space(translate(translate($innerText,'Value',''),':',''))"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:variable>
    <xsl:variable name="processedMessage" select="concat($errMessage, '.',$valueMessage)"/>
    <xsl:if test="contains($errMessage,';')">
        <xsl:call-template name="semiColonMessage">
            <xsl:with-param name="message" select="substring-after($message,';')"/>
            <xsl:with-param name="preparedString" select="concat($preparedString,' ',$processedMessage)"/>
        </xsl:call-template>
    </xsl:if>
    <xsl:if test="not(contains($message,';'))">
        <xsl:value-of select="concat($preparedString,' ',$errMessage)"/>
    </xsl:if>
</xsl:template>
<xsl:template name="colonMessage">
    <xsl:param name="errorMessage"/>
    <xsl:if test="contains($errorMessage,':')">
        <xsl:variable name="message" select="normalize-space(substring-after($errorMessage, ':'))"/>
        <xsl:value-of select="concat('Missing Required Field', '.',$message)"></xsl:value-of>
    </xsl:if>
</xsl:template>

</xsl:stylesheet>


  <!-- ********************************* @author CIBILMaheshwari.Wagish ************************************************** -->