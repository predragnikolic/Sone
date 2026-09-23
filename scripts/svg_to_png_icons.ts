for await (const entry of Deno.readDir("./svg")) {
  console.log(entry.name);

  const promise = []
  promise.push((new Deno.Command("inkscape", {
      args: [
        '--export-type=png',
        `--export-dpi=96`,
        `--export-filename=./d/${entry.name.replace(/\.svg$/, '')}.png`,
        `./svg/${entry.name}`
      ],
  })).output());
  promise.push((new Deno.Command("inkscape", {
      args: [
      '--export-type=png',
        `--export-dpi=192`,
        `--export-filename=./d/${entry.name.replace(/\.svg$/, '')}@2x.png`,
        `./svg/${entry.name}`
      ],
  })).output());
  promise.push((new Deno.Command("inkscape", {
      args: [
        '--export-type=png',
        `--export-dpi=288`,
        `--export-filename=./d/${entry.name.replace(/\.svg$/, '')}@3x.png`,
        `./svg/${entry.name}`
      ],
  })).output());
  await Promise.all(promise)
}
