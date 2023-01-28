FROM node:14-alpine

ADD . ./app

WORKDIR /app

RUN npm install -g @angular/cli@12.2.18 && npm install

EXPOSE 4200


CMD ["ng", "serve", "--host=0.0.0.0", "--disable-host-check"]
