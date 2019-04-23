## 企业微信通知

### 服务组成

组成部分：

- Lambda
- API Gateway
- DynamoDB 


### terraform

- 使用示例

module "wechat-push" {
  source                             = "./modules/wechat-push-lanmuda"
  lambda_function_name               = "wechat-push"
  lambda_push_secretkey              = "调用Lambda程序所需的secretkey"
  lambda_im_ewc_corpid               = "企业微信的corpid"
  lambda_im_ewc_corpsecret           = "企业微信的corpsecret"
  db_table_name                      = "example"
}

### API

**透传企业微信API的参数，不需要关心access_token**

[消息类型的参数说明,详见](https://work.weixin.qq.com/api/doc#90000/90135/90250)