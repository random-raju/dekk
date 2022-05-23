import { Dekk } from "../models/dekk";
import { DekkMetadata } from "../models/dekk-metadata";

export class DekkUtils {
    public static getEmptyDekkMetadata(): DekkMetadata {
        return {
            dekk_id: '',
            dekk_name: '',
            cards: []
        };
    }

    public static getEmptyDekk(): Dekk {
        return {
            tag_name: ''
        } as Dekk;
    }
}