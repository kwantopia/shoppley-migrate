//
//  SLSelectAmountViewController.h
//  shoppleyMerchant
//
//  Created by yod on 6/30/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol SLSelectAmountDelegate <NSObject>
- (void)didSelectAmount:(NSNumber*)amount;
- (void)didselectUnit:(NSNumber*)unit;
@end

@interface SLSelectAmountViewController : TTTableViewController {
    id<SLSelectAmountDelegate> _delegate;
    UITextField* _amountField;
    UISegmentedControl* _unitSelector;
}

@property (nonatomic, assign) id<SLSelectAmountDelegate> delegate;
@property (nonatomic, assign) UITextField* amountField;
@property (nonatomic, assign) UISegmentedControl* unitSelector;

- (void)selectUnit;

@end
