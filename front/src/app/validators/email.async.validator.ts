import { AbstractControl, AsyncValidatorFn } from "@angular/forms";
import { Observable, of } from "rxjs";
import { map } from "rxjs/operators";
import { AuthService } from "../services/auth.service";


export const emailNotExistsAsyncValidator = (userService: AuthService): AsyncValidatorFn => {
    return (control: AbstractControl): Observable<{ [key: string]: any } | null> => {
        if (control.value == '') {
            return of(null);
        }
        else {
            return userService.emailExists(control.value).pipe(
                map((exists) => (exists==false ? { emailnotexists: true } : null))
            );
        }
    };
}

export const emailExistsAsyncValidator = (userService: AuthService): AsyncValidatorFn => {
    return (control: AbstractControl): Observable<{ [key: string]: any } | null> => {
        if (control.value == '') {
            return of(null);
        }
        else {
            return userService.emailExists(control.value).pipe(
                map((exists) => (exists==true ? { emailexists: true } : null))
            );
        }
    };
}