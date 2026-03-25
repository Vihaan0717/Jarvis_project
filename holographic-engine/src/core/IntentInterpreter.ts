export interface Intent {
    action: string;
    params: any;
}

export class IntentInterpreter {
    public interpret(text: string): Intent | null {
        const cmd = text.toLowerCase();
        
        if (cmd.includes("switch particles to")) {
            const shape = cmd.split("to ")[1]?.split(" ")[0];
            return { action: "morph", params: { shape } };
        }
        
        if (cmd.includes("increase particle count")) {
            const count = parseInt(cmd.match(/\d+/)?.[0] || "100000");
            return { action: "setCount", params: { count } };
        }

        if (cmd.includes("simulate")) {
            if (cmd.includes("molecular")) return { action: "simulate", params: { type: "molecular" } };
            if (cmd.includes("fluid")) return { action: "simulate", params: { type: "fluid" } };
        }

        return null;
    }
}
