//
//  LoginViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface LoginViewController : TTTableViewController <UITextFieldDelegate> {
    TTListDataSource *_loginDataSource;
    TTListDataSource *_isLoadingDataSource;
    UITextField *_emailField;
    UITextField *_passwordField;
}

- (void)authenticate;

@end
