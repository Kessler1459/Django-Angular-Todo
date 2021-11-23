import { Category } from "./category";
import { Column } from "./column";
import { User } from "./user";

export class Board {
    id:number;
    owner:User;
    name:string;
    columns:Column[];
    guests:User[];
    categories:Category[];
}
