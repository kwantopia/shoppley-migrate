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

- (TTStyle*)redText {
    return [TTTextStyle styleWithColor:[UIColor redColor] next:nil];
}

@end
