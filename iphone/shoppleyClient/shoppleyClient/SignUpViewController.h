//
//  SignUpViewController.h
//  shoppleyClient
//
//  Created by yod on 7/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SignUpViewController : TTTableViewController <UITextFieldDelegate> {
    TTListDataSource *_signupDataSource;
    UITextField *_emailField;
    UITextField *_phoneField;
    UITextField *_zipcodeField;
    UITextField *_passwordField;
    UITextField *_passwordField1;
}

- (void)signup;

@end
