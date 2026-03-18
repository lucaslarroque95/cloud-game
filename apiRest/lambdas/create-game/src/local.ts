import { handler } from "./handler";

(async () => {
  const result = await handler({
    body: JSON.stringify({}),
  });

  console.log(result);
})();