//
//  SLTableItem.h
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLRightValueTableItem : TTTableCaptionItem {
    
}

+ (id)itemWithText:(NSString *)text value:(NSString *)value;
+ (id)itemWithText:(NSString *)text value:(NSString *)value URL:(NSString *)URL;

@end

@interface SLStarsTableItem : TTTableItem {
    NSNumber* _numberOfStars;
}

@property (nonatomic, copy) NSNumber* numberOfStars;

+ (id)itemWithNumberofStars:(NSNumber*)numberOfStars;

@end

@interface SLRightStarsTableItem : TTTableTextItem {
    NSNumber* _numberOfStars;
}

+ (id)itemWithText:(NSString *)text numberOfStars:(NSNumber *)numberOfStars URL:(NSString *)URL;

@property (nonatomic, copy) NSNumber* numberOfStars;

@end
