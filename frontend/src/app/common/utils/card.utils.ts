import { Card } from "../models/card";
import * as _ from 'lodash';
import { CardEditable } from "../models/card-editable";

export class CardUtils {
    static OFFSET_LOAD_NUM_OF_CARDS = 10;
    static STUDY_SESSION_DEFAULT_MAX_NUM_OF_CARDS = 200;
    static DEFAULT_TEXT_HIGHLIGHT_COLOR = '#f3f57f';
    static HIGHLIGHTER_OPEN_TAG = '<span style="background-color: ' + CardUtils.DEFAULT_TEXT_HIGHLIGHT_COLOR +'">'
    static HIGHLIGHTER_CLOSE_TAG = '</span>';
    
    public static getCardCategoryText(card: Card): string {
        let cardCategory = '';
        _.forEach(card.tags, (element: any) => {
            if (element.value === 1)
            cardCategory = element.key + '/';
        });
        cardCategory += card.title;
        return cardCategory;
    }

    public static getCardDekkText(card: Card): string {
        return this.getCardCategoryText(card) + ' / ' + card.dekk_name;
    }

    public static getDummyCard(): Card {
        return {
            card_id: '',
            account_id: -1,
            title: "Invalid Card",
            category: "Invalid",
            dekk_name: "Invalid",
            highlighted_keywords: [],
            image_links: [],
            tags: [],
            content_on_front: "Invalid Card",
            content_on_back: "Invalid Card",
            is_bookmarked: false
        };
    }

    public static getWaitCard(): Card {
        return {
            card_id: '-1',
            account_id: -1,
            title: "",
            category: "",
            dekk_name: "",
            highlighted_keywords: [],
            image_links: [],
            tags: [],
            content_on_front: "Please wait",
            content_on_back: "Please wait"
        };
    }

    public static getEmptyEditableCard(): CardEditable {
        return {
            card_id: '-1',
            account_id: -1,
            title: "",
            category: "",
            dekk_name: "",
            highlighted_keywords: [],
            tags: ["NEET"],
            content_on_front: "",
            content_on_back: ""
        };
    }
}