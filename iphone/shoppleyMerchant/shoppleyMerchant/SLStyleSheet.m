//
//  SLStyleSheet.m
//  shoppleyMerchant
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLStyleSheet.h"


@implementation SLStyleSheet

- (UIColor*)tableGroupedBackgroundColor {
	return RGBCOLOR(228, 230, 235); // light-blue gray
}

- (TTStyle*)greenButton:(UIControlState)state {
    TTShape* shape = [TTRoundedRectangleShape shapeWithRadius:4.5];
    UIColor* tintColor = RGBCOLOR(0, 187, 0);
    return [TTSTYLESHEET toolbarButtonForState:state shape:shape tintColor:tintColor font:[UIFont boldSystemFontOfSize:16]];
}

- (TTStyle*)redText {
    return [TTTextStyle styleWithColor:[UIColor redColor] next:nil];
}

@end
