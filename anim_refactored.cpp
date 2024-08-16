void Actor::PickAnimations(float movementSpeed, float turnSpeed)
{
   if (!this->IsDying() && !this->GetKnockedState()) // [COLLAPSED LOCAL DECLARATIONS. PRESS KEYPAD CTRL-"+" TO EXPAND]
   {
       if (this == g_thePlayer && !PlayerCharacter__IsNotFirstPerson(g_thePlayer))
       {
           DebugLog("AI: Don't call Actor::PickAnimations on the 1st person pc.");
           return;
       }
       animData = this->GetAnimData();
       charController = MobileObject::GetCharacterController(this);
       if (animData)
       {
           if (this->baseProcess && charController)
           {
               if (!BaseProcess::GetProcessLevel_Tile::GetParent_GetUnk028(this->baseProcess))
                   nullsub_483710(this->baseProcess);
               AnimSequenceElement = AnimData::GetAnimSequenceElement(animData, kSequence_Weapon);
               if (AnimSequenceElement && (TESAnimGroup::GetMoveType(BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement)) == kAnimMoveType_Sneaking) != Actor::IsSneaking(this) && BSAnimGroupSequence::GetState(AnimSequenceElement) == kAnimState_Animating && TESAnimGroup::IsAimAnim(BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement)))
               {
                   NthSequenceGroupID = AnimData::GetNthSequenceGroupID(animData, kSequence_Weapon);
                   TESAnimGroup = BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement);
                   SequenceGroup = TESAnimGroup::GetSequenceGroup(TESAnimGroup);
                   if (NthSequenceGroupID != Actor__GetAnimKey(this, SequenceGroup, 0, 0, 0))
                       AnimData::EndsSequenceIfNotAim(animData, kSequence_Weapon, 0);
               }
               else
               {
                   v9 = AnimData::GetNthSequenceGroupID(animData, kSequence_Weapon);
                   if (AnimGroupID::GetGroupID(v9) == kAnimGroup_AttackLoop || AnimGroupID::GetGroupID(AnimData::GetNthSequenceGroupID(animData, kSequence_Weapon)) == kAnimGroup_AttackLoopIS)
                   {
                       if (this->baseProcess->GetAttackLoopTimeRemaining_111() == 0.0 && BSAnimGroupSequence::GetState(AnimSequenceElement) == kAnimState_Animating)
                       {
                           AnimData::EndsSequenceIfNotAim(animData, kSequence_Weapon, 0);
                       }
                   }
               }
               if (this == g_thePlayer)
               {
                   firstPersonAnimData = PlayerCharacter::GetAnimData(g_thePlayer, kPlayerAnimData_1st);
                   AnimSequenceElement = AnimData::GetAnimSequenceElement(firstPersonAnimData, kSequence_Weapon);
                   if (AnimSequenceElement && (TESAnimGroup::GetMoveType(BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement)) == 1) != Actor::IsSneaking(this) && BSAnimGroupSequence::GetState(AnimSequenceElement) == kAnimState_Animating && TESAnimGroup::IsAimAnim(BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement)))
                   {
                       v14 = AnimData::GetNthSequenceGroupID(firstPersonAnimData, kSequence_Weapon);
                       v15 = BSAnimGroupSequence::GetTESAnimGroup(AnimSequenceElement);
                       v16 = TESAnimGroup::GetSequenceGroup(v15);
                       if (v14 != Actor__GetAnimKey(this, v16, 0, 0, firstPersonAnimData))
                           AnimData::EndsSequenceIfNotAim(firstPersonAnimData, kSequence_Weapon, 0);
                   }
                   else
                   {
                       v17 = AnimData::GetNthSequenceGroupID(firstPersonAnimData, kSequence_Weapon);
                       if (AnimGroupID::GetGroupID(v17) == kAnimGroup_AttackLoop || AnimGroupID::GetGroupID(AnimData::GetNthSequenceGroupID(firstPersonAnimData, kSequence_Weapon)) == kAnimGroup_AttackLoopIS)
                       {
                           if (this->baseProcess->GetAttackLoopTimeRemaining_111() == 0.0 && BSAnimGroupSequence::GetState(AnimSequenceElement) == kAnimState_Animating)
                           {
                               AnimData::EndsSequenceIfNotAim(firstPersonAnimData, kSequence_Weapon, 0);
                           }
                       }
                   }
               }
               v167 = 1.0;
               movementSpeedMult = 0.0;
               wantsWeaponOutCancelVATS = Actor::GetWantsWeaponOut_IfSwimmingCancelVATS(this);
               animGroup = kAnimGroup_Idle;
               animMoveType = kAnimMoveType_Walking;
               animHandType = kAnimHandType_H2H;
               animAction = kAnimAction_None;
               v159 = AnimData::GetAnimSequenceElement(animData, kSequence_Movement);
               v161 = this->GetBipedAnim();
               weapInfo = this->baseProcess->GetWeaponInfo();
               if (weapInfo)
                   Flags = TESForm::GetFlags(weapInfo);
               else
                   Flags = 0;
               weap = Flags;
               moveFlags = Actor__GetMovementFlags(this);
               currentAnimAction = this->baseProcess->GetCurrentAnimAction();
               sitSleepState = this->baseProcess->GetSitSleepState();
               furnitureData = this->baseProcess->GetFurnitureData();
               if (currentAnimAction != kAnimAction_None)
               {
                   if (this->baseProcess->GetCurrentSequence() && BSAnimGroupSequence::GetState(this->baseProcess->GetCurrentSequence()))
                   {
                       switch (currentAnimAction) {
                           case kAnimAction_Equip_Weapon:
                           case kAnimAction_Unequip_Weapon:
                               if (this->baseProcess->IsWeaponOut() != (currentAnimAction == kAnimAction_Equip_Weapon) && AnimData::GetSequenceState1(animData, kSequence_Weapon) >= kSeqState_HitOrDetach)
                               {
                                   animData_1 = animData;
                                   BipedAnim = v161;
                                   v128 = 1;
                                   if (this == g_thePlayer)
                                       v128 = 2;
                                   this->baseProcess->SetWeaponOut();
                                   while (v128)
                                   {
                                       if (this == g_thePlayer && v128 == 1)
                                       {
                                           animData_1 = PlayerCharacter::GetAnimData(g_thePlayer, kPlayerAnimData_1st);
                                           BipedAnim = PlayerCharacter::GetBipedAnim(g_thePlayer, 1);
                                       }
                                       if (!this->baseProcess->IsWeaponOut() && weap && animData_1)
                                       {
                                           if (AnimData_KFModel::GetAnimGroup08(animData_1))
                                           {
                                               AnimGroup08 = AnimData_KFModel::GetAnimGroup08(animData_1);
                                               WeaponType = TESObjectWEAP_getWeaponType(weap);
                                               sub_8D6A80(g_weaponTypeToAnim[WeaponType], AnimGroup08);
                                           }
                                       }
                                       this->baseProcess->SetEquippedWeaponPosition();
                                       --v128;
                                   }
                                   Actor::AimWeapon(this, 0, 0, 0);
                                   if (this == g_thePlayer)
                                   {
                                       if (currentAnimAction)
                                       {
                                           sub_C74890(this->ragDollController, 0, 0);
                                           sub_C74890(this->ragDollController, 1, 0);
                                           sub_8978F0(this->ragDollController, 1, 1);
                                           sub_8978F0(this->ragDollController, 1, 1);
                                       }
                                       else
                                       {
                                           v126 = 0;
                                           v124 = 0;
                                           v46 = this->baseProcess->GetWeaponBone();
                                           v125 = NiNode::GetNthChild_BoundCheck(v46, 0);
                                           if (v125)
                                           {
                                               g_ni_BSX = get_g_ni_BSX();
                                               Extra = NiNode::GetExtra(v125, g_ni_BSX);
                                               if (Extra)
                                               {
                                                   if (sub_8978D0(Extra))
                                                   {
                                                       g_niGrabLeft = get_g_niGrabLeft();
                                                       v126 = v125->GetObjectByName(v125, g_niGrabLeft);
                                                       g_niGrabRight = get_g_niGrabRight();
                                                       v124 = v125->GetObjectByName(v125, g_niGrabRight);
                                                   }
                                               }
                                           }
                                           sub_C74890(this->ragDollController, 0, v126);
                                           sub_C74890(this->ragDollController, 1, v124);
                                       }
                                   }
                                   this->baseProcess->Unk_160();
                                   if (this->baseProcess->IsWeaponOut() && this->baseProcess->Unk_15D())
                                   {
                                       v50 = this->baseProcess->Unk_15D();
                                       MagicShaderHitEffectForActor = ProcessManager::GetMagicShaderHitEffectForActor(&g_processManager, this, v50);
                                       if (MagicShaderHitEffectForActor)
                                           sub_8216C0(MagicShaderHitEffectForActor);
                                       if (weap)
                                       {
                                           EnchantmentItem = TESForm::GetEnchantmentItem(weap);
                                           if (EnchantmentItem)
                                               formMagic = &EnchantmentItem->magicItem;
                                           else
                                               formMagic = 0;
                                           if (!formMagic)
                                           {
                                               ExtraPoison = ContChangesEntry__GetExtraPoison(weapInfo);
                                               if (ExtraPoison)
                                                   formMagic = ExtraPoison + 48;
                                               else
                                                   formMagic = 0;
                                           }
                                           if (formMagic)
                                           {
                                               PlaySoundAtActorPos(this, dst, "WPNBlade1HandEquipEnchanted", 0, 0x40000102, 1);
                                               nullsub_483710(dst);
                                           }
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_Attack:
                               curTPSAnim = this->baseProcess->GetCurrentSequence();
                               v30 = BSAnimGroupSequence::GetTESAnimGroup(curTPSAnim);
                               sequenceType = g_animSequenceTypes[9 * TESAnimGroup::GetSequenceGroup(v30)];
                               if (sequenceType == kSequence_LeftArm)
                               {
                                   if (AnimData::GetSequenceState1(animData, kSequence_LeftArm) == kSeqState_HitOrDetach)
                                   {
                                       v38 = AnimData::GetNthSequenceGroupID(animData, kSequence_LeftArm);
                                       v98 = g_animKeyTypes[9 * AnimGroupID::GetGroupID(v38)];
                                       if (v98 >= kAnimKeyType_Attack && v98 <= kAnimKeyType_PowerAttackOrPipboy)
                                       {
                                           if (this->magicCaster.__vftable->GetMagicItem160(&this->magicCaster))
                                               MagicCaster_815870(&this->magicCaster, 0);
                                           v39 = this->baseProcess->GetCurrentSequence();
                                           Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v39);
                                       }
                                   }
                               }
                               else if (sequenceType == kSequence_Weapon)
                               {
                                   sequence = this->baseProcess->GetCurrentSequence();
                                   animGroup_1 = BSAnimGroupSequence::GetTESAnimGroup(sequence);
                                   if (g_animKeyTypes[9 * TESAnimGroup::GetSequenceGroup(animGroup_1)] != kAnimKeyType_LoopingSequenceOrAim && AnimData::GetSequenceState1(animData, kSequence_Weapon) == kSeqState_HitOrDetach)
                                   {
                                       v33 = AnimData::GetNthSequenceGroupID(animData, kSequence_Weapon);
                                       v102 = g_animKeyTypes[9 * AnimGroupID::GetGroupID(v33)];
                                       if (v102 == kAnimKeyType_Attack)
                                       {
                                           if (this->magicCaster.__vftable->GetMagicItem160(&this->magicCaster))
                                           {
                                               MagicCaster_815870(&this->magicCaster, 0);
                                           }
                                           else if (!weap || !TESObjectWEAP::IsAutomatic(weap))
                                           {
                                               if (weap && TESObjectWEAP_IsNonMeleeWeapon(weap))
                                               {
                                                   this->baseProcess->SetQueuedIdleFlag();
                                               }
                                               else if (this == g_thePlayer || Actor__GetIsInCombat(this) || (v130 = MobileObject::GetBaseProcess(this)->__vftable->GetCurrentPackage(MobileObject::GetBaseProcess(this))) != 0 && (TESPackage__GetType(v130) == kPackageType_UseItemAt || TESPackage__GetType(v130) == kPackageType_UseWeapon))
                                               {
                                                   sub_899200(this, 0, 1);
                                               }
                                               else
                                               {
                                                   sub_899200(this, 0, 0);
                                               }
                                           }
                                           if (Actor::IsDoingAttackAnimation(this))
                                           {
                                               if (!weap || TESObjectWEAP::IsAutomatic(weap) || TESObjectWEAP_IsMeleeWeapon(weap))
                                               {
                                                   v37 = this->baseProcess->GetCurrentSequence();
                                                   Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v37);
                                               }
                                               else
                                               {
                                                   v36 = this->baseProcess->GetCurrentSequence();
                                                   Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Eject, v36); // sequenceState stays 0 for duration of reload loop->walk => delayed fire bug
                                               }
                                           }
                                       }
                                       else if (v102 == kAnimKeyType_PowerAttackOrPipboy)
                                       {
                                           if (this == g_thePlayer || Actor__GetIsInCombat(this))
                                           {
                                               sub_899200(this, 1, 1);
                                           }
                                           else
                                           {
                                               v101 = MobileObject::GetBaseProcess(this);
                                               v131 = v101->__vftable->GetCurrentPackage(v101);
                                               if (v131 && (TESPackage__GetType(v131) == kPackageType_UseItemAt || TESPackage__GetType(v131) == kPackageType_UseWeapon) && !MobileObject::GetBaseProcess(this)->__vftable->IsUsingThrownWeapon(MobileObject::GetBaseProcess(this))) // fires the weapon
                                               {
                                                   sub_899200(this, 0, 1);
                                               }
                                               else
                                               {
                                                   sub_899200(this, 1, 0);
                                               }
                                           }
                                           if (Actor::IsDoingAttackAnimation(this))
                                           {
                                               v35 = this->baseProcess->GetCurrentSequence();
                                               Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v35);
                                           }
                                       }
                                       else if (v102 == kAnimKeyType_SpinAttack && this->baseProcess->GetAttackLoopTimeRemaining_111() == 0.0)
                                       {
                                           v34 = this->baseProcess->GetCurrentSequence();
                                           Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v34);
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_Attack_Eject:
                               v40 = this->baseProcess->GetCurrentSequence();
                               v41 = BSAnimGroupSequence::GetTESAnimGroup(v40);
                               if (g_animSequenceTypes[9 * TESAnimGroup::GetSequenceGroup(v41)] == kSequence_Weapon)
                               {
                                   if (weap)
                                   {
                                       v42 = this->baseProcess->GetCurrentSequence();
                                       v43 = BSAnimGroupSequence::GetTESAnimGroup(v42);
                                       if (g_animKeyTypes[9 * TESAnimGroup::GetSequenceGroup(v43)] != kAnimKeyType_LoopingSequenceOrAim && AnimData::GetSequenceState1(animData, kSequence_Weapon) == kSeqState_EjectOrUnequipEnd)
                                       {
                                           this->baseProcess->SetQueuedIdleFlag();
                                           v44 = this->baseProcess->GetCurrentSequence();
                                           Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v44);
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_Attack_Throw:
                               releaseKeyID = kSeqState_EjectOrUnequipEnd;
                               currSequenceID = this->baseProcess->GetCurrentSequence();
                               v138 = BSAnimGroupSequence::GetTESAnimGroup(currSequenceID);
                               v136 = TESAnimGroup::GetSequenceGroup(v138);
                               keyType = g_animKeyTypes[9 * v136];
                               if (keyType == kAnimKeyType_AttackThrow)
                                   goto LABEL_63;
                               if (keyType == kAnimKeyType_PlaceMine)
                               {
                                   releaseKeyID = kSeqState_HitOrDetach;
                               LABEL_63:
                                   if (AnimData::GetSequenceState1(animData, kSequence_Weapon) == releaseKeyID)
                                   {
                                       if (weap && !TESObjectWEAP_IsMeleeWeapon(weap))
                                           this->baseProcess->SetQueuedIdleFlag();
                                       if (Actor::IsDoingAttackAnimation(this))
                                       {
                                           v25 = this->baseProcess->GetCurrentSequence();
                                           Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Throw_Attach, v25);
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_Attack_Throw_Attach:
                               attachKeyID = 3;
                               v26 = this->baseProcess->GetCurrentSequence();
                               v27 = BSAnimGroupSequence::GetTESAnimGroup(v26);
                               v104 = g_animKeyTypes[9 * TESAnimGroup::GetSequenceGroup(v27)];
                               if (v104 == kAnimKeyType_AttackThrow)
                                   goto LABEL_73;
                               if (v104 == kAnimKeyType_PlaceMine)
                               {
                                   attachKeyID = 2;
                               LABEL_73:
                                   if (AnimData::GetSequenceState1(animData, kSequence_Weapon) == attachKeyID)
                                   {
                                       if (weap && !TESObjectWEAP_IsMeleeWeapon(weap))
                                       {
                                           v132 = animData;
                                           v134 = v161;
                                           v133 = 1;
                                           if (this == g_thePlayer)
                                               v133 = 2;
                                           while (v133)
                                           {
                                               if (this == g_thePlayer && v133 == 1)
                                               {
                                                   v132 = PlayerCharacter::GetAnimData(g_thePlayer, kPlayerAnimData_1st);
                                                   v134 = PlayerCharacter::GetBipedAnim(g_thePlayer, 1);
                                               }
                                               this->baseProcess->SetEquippedWeaponPosition();
                                               --v133;
                                           }
                                       }
                                       if (Actor::IsDoingAttackAnimation(this))
                                       {
                                           v28 = this->baseProcess->GetCurrentSequence();
                                           Actor::SetAnimActionAndSequence(this, kAnimAction_Attack_Follow_Through, v28);
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_Dodge:
                               movementSpeedMult = Actor::GetWalkSpeed(this);
                               break;
                           case kAnimAction_Wait_For_Lower_Body_Anim:
                               if (sitSleepState == kSitSleepState_Normal)
                               {
                                   ContextHkState = bhkCharacterController::GetContextHkState(charController);
                                   if (ContextHkState == kCharControllerState_Jumping)
                                       goto LABEL_203;
                                   if (ContextHkState == kCharControllerState_InAir)
                                   {
                                       if (v159)
                                       {
                                           v51 = BSAnimGroupSequence::GetTESAnimGroup(v159);
                                           if (TESAnimGroup::IsJumping(v51))
                                               Actor::SetAnimActionAndSequence(this, kAnimAction_None, 0);
                                       }
                                   }
                               }
                               break;
                           case kAnimAction_ReloadLoop:
                               anim = this->baseProcess->GetCurrentSequence();
                               animGroup_2 = BSAnimGroupSequence::GetTESAnimGroup(anim);
                               sequenceType_ = TESAnimGroup::GetSequenceGroup(animGroup_2);
                               if (wantsWeaponOutCancelVATS && !this->baseProcess->IsWeaponOut() && weap && weapInfo)
                               {
                                   HasWeaponMod = ContChangesEntry::HasWeaponMod(weapInfo, kWeaponModEffect_IncreaseClipCapacity);
                                   this->Reload_();
                                   animAction = -1;
                                   Actor::SetAnimActionAndSequence(this, kAnimAction_None, 0);
                               }
                               else if (sequenceType_ > kAnimGroup_ReloadZStart)
                               {
                                   if (AnimData::GetSequenceState1(animData, kSequence_Weapon) == kAnimState_Animating)
                                       this->baseProcess->SetQueuedIdleFlag();
                               }
                               else
                               {
                                   SequenceOffsetPlusTimePassed = AnimData::GetSequenceOffsetPlusTimePassed(animData, anim);
                                   v22 = BSAnimGroupSequence::GetTESAnimGroup(anim);
                                   if (TESAnimGroup::GetTimeForAction(v22, 1u) <= SequenceOffsetPlusTimePassed)
                                   {
                                       v23 = ContChangesEntry::HasWeaponMod(weapInfo, kWeaponModEffect_IncreaseClipCapacity);
                                       a2a = TESObjectWEAP::GetReloadAnimGroup(weap, v23);
                                       AnimKey = Actor__GetAnimKey(this, a2a, 0, 0, 0);
                                       if (AnimGroupID::GetGroupID(AnimKey) == a2a)
                                       {
                                           v141 = this->GetAnimData();
                                           AnimData::PlayAnimGroup(v141, AnimKey, 1, -1, -1);
                                           if (this == g_thePlayer)
                                               g_thePlayer->PlayFirstPersonAnimation();
                                       }
                                       animAction = kAnimAction_ReloadLoop;
                                       v24 = AnimData::GetAnimSequenceElement(animData, kSequence_Weapon);
                                       Actor::SetAnimActionAndSequence(this, kAnimAction_ReloadLoop, v24);
                                   }
                               }
                               break;
                           default:
                               break;
                       }
                   }
                   else
                   {
                       if (AnimData::GetAnimSequenceElement(animData, kSequence_LeftArm))
                       {
                           v52 = AnimData::GetNthSequenceGroupID(animData, kSequence_LeftArm);
                           if (AnimGroupID::GetGroupID(v52) == kAnimGroup_BlockIdle)
                           {
                               animAction = kAnimAction_Block;
                               v53 = AnimData::GetAnimSequenceElement(animData, kSequence_LeftArm);
                               Actor::SetAnimActionAndSequence(this, kAnimAction_Block, v53);
                           }
                       }
                       if (weap)
                       {
                           if (!TESObjectWEAP::NoJamAfterReload(weap) && currentAnimAction == kAnimAction_Reload)
                           {
                               v54 = this->baseProcess->GetCurrentSequence();
                               v55 = BSAnimGroupSequence::GetTESAnimGroup(v54);
                               v56 = TESAnimGroup::GetSequenceGroup(v55);
                               if (AnimGroup::IsReload(v56))
                               {
                                   v120 = this->baseProcess->GetEquippedWeaponHealthBracket();
                                   if (GetWeaponReloadJamChance(v120) > 0.0)
                                   {
                                       WeaponReloadJamChance = GetWeaponReloadJamChance(v120);
                                       if (RNG::IsRandomDecimalBelow(WeaponReloadJamChance))
                                       {
                                           animGroupID = TESObjectWEAP::GetReloadAnimGroup(weap, 0) + 23;
                                           v119 = Actor__GetAnimKey(this, animGroupID, 0, 0, 0);
                                           if (AnimGroupID::GetGroupID(v119) == animGroupID)
                                           {
                                               animAction = kAnimAction_Reload;
                                               Actor::PlayAttackAnim(this, animGroupID, animData);
                                               v57 = AnimData::GetAnimSequenceElement(animData, kSequence_Weapon);
                                               Actor::SetAnimActionAndSequence(this, kAnimAction_Reload, v57);
                                               this->PlayFirstPersonAnimation();
                                           }
                                       }
                                   }
                               }
                           }
                       }
                       if (animAction == -1)
                           LABEL_203:
                       Actor::SetAnimActionAndSequence(this, kAnimAction_None, 0);
                   }
               }
               if (animAction == -1)
               {
                   if (sitSleepState == kSitSleepState_Normal)
                   {
                       switch (currentAnimAction) {
                           case 0xFFFFFFFF:
                           case kAAP1_Unequip_Weapon:
                           case kAAP1_Attack_Eject:
                           case kAAP1_Dodge:
                               v92 = bhkCharacterController::GetContextHkState(charController);
                               if (v92)
                               {
                                   if (v92 == kCharControllerState_Jumping)
                                   {
                                       animGroup = kAnimGroup_JumpLoop;
                                   }
                                   else if (v92 == kCharControllerState_InAir)
                                   {
                                       FallTimeElapsed = bhkCharacterController::GetFallTimeElapsed(charController);
                                       if (*GameSettings::GetFloatValueAddr(gs_fJumpAnimDelay_HAVOK) < FallTimeElapsed || v159 && TESAnimGroup::IsJumping(BSAnimGroupSequence::GetTESAnimGroup(v159)))
                                       {
                                           animGroup = kAnimGroup_JumpLoop;
                                       }
                                   }
                               }
                               else if (v159)
                               {
                                   v59 = BSAnimGroupSequence::GetTESAnimGroup(v159);
                                   if (TESAnimGroup::IsJumping(v59) || TESAnimGroup::GetSequenceGroup(BSAnimGroupSequence::GetTESAnimGroup(v159)) == kAnimGroup_JumpStart)
                                   {
                                       currentAnimAction = -1;
                                       animAction = kAnimAction_Wait_For_Lower_Body_Anim;
                                       if ((moveFlags & kMoveFlag_Forward) != 0)
                                       {
                                           animGroup = kAnimGroup_JumpLandForward;
                                       }
                                       else if ((moveFlags & kMoveFlag_Backward) != 0)
                                       {
                                           animGroup = kAnimGroup_JumpLandBackward;
                                       }
                                       else if ((moveFlags & kMoveFlag_Left) != 0)
                                       {
                                           animGroup = kAnimGroup_JumpLandLeft;
                                       }
                                       else if ((moveFlags & kMoveFlag_Right) != 0)
                                       {
                                           animGroup = kAnimGroup_JumpLandRight;
                                       }
                                       else
                                       {
                                           animGroup = kAnimGroup_JumpLand;
                                       }
                                       AnimData::SetByte120To1(animData);
                                       CycleType__Unk24 = BSAnimGroupSequence::GetCycleType__Unk24(&charController->chrListener);
                                       Actor::PlayLandJumpSound(this, CycleType__Unk24);
                                   }
                               }
                               break;
                           default:
                               break;
                       }
                       if (wantsWeaponOutCancelVATS && !this->baseProcess->IsWeaponOut() && currentAnimAction == -1 && Actor_8843A0(this))
                       {
                           if (!AnimData::IsNoIdlePlaying(animData))
                               ExtraDataAnim::SetQueuedAnimAsCurrent(animData, 1, 1);
                           animGroup = kAnimGroup_Equip;
                           animAction = kAnimAction_Equip_Weapon;
                       }
                   }
                   if (!wantsWeaponOutCancelVATS && this->baseProcess->IsWeaponOut() && currentAnimAction == -1 && !this->Unk_8D() && !this->IsDying() && !this->GetKnockedState() && !Actor::GetIsRestrained(this) && !Actor::GetIsUnConscious(this))
                   {
                       animGroup = kAnimGroup_Unequip;
                       animAction = kAnimAction_Unequip_Weapon;
                   }
               }
               if (!this->GetActorType() && (wantsWeaponOutCancelVATS || Actor__GetIsInCombat(this)) || this->baseProcess->IsWeaponOut() || animAction <= 1)
               {
                   if (weapInfo)
                   {
                       v62 = TESForm::GetFlags(weapInfo);
                       animHandType = g_weaponTypeToAnim[TESObjectWEAP_getWeaponType(v62)];
                   }
                   else
                   {
                       animHandType = kAnimHandType_1HM;
                   }
               }
               if ((moveFlags & kMoveFlag_Swimming) != 0)
               {
                   animMoveType = kAnimMoveType_Swimming;
               }
               else if ((moveFlags & kMoveFlag_Flying) != 0)
               {
                   animMoveType = kAnimMoveType_Flying;
               }
               else if ((moveFlags & kMoveFlag_Sneaking) != 0)
               {
                   animMoveType = kAnimMoveType_Sneaking;
               }
               if (animGroup)
               {
                   if (animGroup == kAnimGroup_JumpLoop && (moveFlags & (kMoveFlag_Right | kMoveFlag_Left | kMoveFlag_Backward | kMoveFlag_Forward)) != 0)
                   {
                       if ((moveFlags & kMoveFlag_Forward) != 0)
                       {
                           animGroup = kAnimGroup_JumpLoopForward;
                       }
                       else if ((moveFlags & kMoveFlag_Backward) != 0)
                       {
                           animGroup = kAnimGroup_JumpLoopBackward;
                       }
                       else if ((moveFlags & kMoveFlag_Left) != 0)
                       {
                           animGroup = kAnimGroup_JumpLoopLeft;
                       }
                       else if ((moveFlags & kMoveFlag_Right) != 0)
                       {
                           animGroup = kAnimGroup_JumpLoopRight;
                       }
                   }
               }
               else
               {
                   switch (sitSleepState) {
                       case kSitSleepState_WaitingForSitAnim:
                       case kSitSleepState_WaitingForSleepAnim:
                           if ((sub_4985B0(animData) || AnimData::IsNoIdlePlaying(animData)) && (!furnitureData || furnitureData->byte0E <= 0x14u))
                           {
                               animGroup = kAnimGroup_DynamicIdle;
                           }
                           break;
                       case kSitSleepState_Sitting:
                       case kSitSleepState_WantToStand:
                       case kSitSleepState_Sleeping:
                       case kSitSleepState_WantToWake:
                           if (this != g_thePlayer || !dereference(&PlayerCharacter::GetAnimData(g_thePlayer, kPlayerAnimData_1st)->idleAnimQueued))
                           {
                               if (!furnitureData || furnitureData->byte0E <= 0x14u)
                                   animGroup = kAnimGroup_DynamicIdle;
                           }
                           break;
                       default:
                           break;
                   }
                   v167 = movementSpeed;
                   if ((moveFlags & (kMoveFlag_Right | kMoveFlag_Left | kMoveFlag_Backward | kMoveFlag_Forward)) != 0)
                   {
                       if ((moveFlags & kMoveFlag_Running) != 0)
                       {
                           if ((moveFlags & 1) != 0)
                           {
                               animGroup = kAnimGroup_FastForward;
                           }
                           else if ((moveFlags & 2) != 0)
                           {
                               animGroup = kAnimGroup_FastBackward;
                           }
                           else if ((moveFlags & 4) != 0)
                           {
                               animGroup = kAnimGroup_FastLeft;
                           }
                           else if ((moveFlags & 8) != 0)
                           {
                               animGroup = kAnimGroup_FastRight;
                           }
                           if (this->GetActorType())
                               movementSpeedMult = Actor::GetRunSpeedMult(this);
                           else
                               movementSpeedMult = Actor::GetWalkSpeed(this);
                       }
                       else if ((moveFlags & (kMoveFlag_Slide | kMoveFlag_Fall | kMoveFlag_Flying | kMoveFlag_Jump | kMoveFlag_Swimming | kMoveFlag_Sneaking | kMoveFlag_Running | kMoveFlag_Walking)) != 0)
                       {
                           if ((moveFlags & kMoveFlag_Forward) != 0)
                           {
                               animGroup = kAnimGroup_Forward;
                           }
                           else if ((moveFlags & kMoveFlag_Backward) != 0)
                           {
                               animGroup = kAnimGroup_Backward;
                           }
                           else if ((moveFlags & kMoveFlag_Left) != 0)
                           {
                               animGroup = kAnimGroup_Left;
                           }
                           else if ((moveFlags & kMoveFlag_Right) != 0)
                           {
                               animGroup = kAnimGroup_Right;
                           }
                           movementSpeedMult = Actor::GetWalkSpeed(this);
                       }
                   }
                   else if ((moveFlags & kMoveFlag_TurnLeft) != 0)
                   {
                       animGroup = kAnimGroup_TurnLeft;
                   }
                   else if ((moveFlags & kMoveFlag_TurnRight) != 0)
                   {
                       animGroup = kAnimGroup_TurnRight;
                   }
               }
               if (animAction == -1 || currentAnimAction == -1)
               {
                   if (movementSpeedMult < 1.0 && animGroup >= kAnimGroup_Forward && animGroup <= kAnimGroup_TurnRight && animGroup != kAnimGroup_TurnLeft && animGroup != kAnimGroup_TurnRight)
                   {
                       if (this == g_thePlayer)
                           g_thePlayer->GetIsOverencumbered();
                       animGroup = kAnimGroup_Idle;
                   }
                   isPowerArmor = (Actor::Process::GetByte12A(this) || Actor::Process::GetByte128(this));
                   groupID_3 = Anim_Concat_MoveType_HandType_Group_PowerArmor(animMoveType, animHandType, animGroup, isPowerArmor);
                   groupID_1 = AnimData::495740(animData, groupID_3, 0);
                   v150 = AnimGroupID::GetGroupID(groupID_1);
                   if (animAction != -1 && animGroup != v150)
                   {
                       if (animAction == 1)
                       {
                           v89 = MobileObject::GetBaseProcess(this);
                           v89->__vftable->SetWeaponOut(v89, this, 0);
                       }
                       animAction = -1;
                   }
                   animGroup = v150;
                   if (currentAnimAction != -1 && this->baseProcess->GetCurrentSequence() && AnimData::GetAnimSequenceElement(animData, g_animSequenceTypes[9 * animGroup]) == this->baseProcess->GetCurrentSequence())
                   {
                       if (currentAnimAction == kAnimAction_Force_Script_Anim)
                       {
                           groupID_1 = AnimData::GetNthSequenceGroupID(animData, kSequence_Movement);
                           if (this->GetActorType())
                           {
                               switch (AnimGroupID::GetGroupID(groupID_1)) {
                                   case kAnimGroup_Backward:
                                   case kAnimGroup_Left:
                                   case kAnimGroup_Right:
                                   case kAnimGroup_DodgeForward:
                                   case kAnimGroup_DodgeBack:
                                   case kAnimGroup_DodgeLeft:
                                   case kAnimGroup_DodgeRight:
                                       groupID_1 = ((groupID_1 & ~0xFF) | kAnimGroup_Forward);
                                       break;
                                   case kAnimGroup_FastBackward:
                                   case kAnimGroup_FastLeft:
                                   case kAnimGroup_FastRight:
                                       groupID_1 = ((groupID_1 & ~0xFF) | kAnimGroup_FastForward);
                                       break;
                                   default:
                                       break;
                               }
                           }
                           else
                           {
                               groupID_1 = ((groupID_1 & 0xFF00) | 3);
                           }
                           switch (AnimGroupID::GetGroupID(groupID_1)) {
                               case kAnimGroup_Forward:
                               case kAnimGroup_Backward:
                               case kAnimGroup_Left:
                               case kAnimGroup_Right:
                               case kAnimGroup_DodgeForward:
                               case kAnimGroup_DodgeBack:
                               case kAnimGroup_DodgeLeft:
                               case kAnimGroup_DodgeRight:
                                   movementSpeedMult = Actor::GetWalkSpeed(this);
                                   goto LABEL_344;
                               case kAnimGroup_FastForward:
                               case kAnimGroup_FastBackward:
                               case kAnimGroup_FastLeft:
                               case kAnimGroup_FastRight:
                                   movementSpeedMult = Actor::GetRunSpeedMult(this);
                                   goto LABEL_344;
                               case kAnimGroup_TurnLeft:
                               case kAnimGroup_TurnRight:
                                   AnimData::SetMovementSpeedMult(animData, turnSpeed);
                                   return;
                               default:
                               LABEL_344:
                                   PlayingAnimGroupMovementVectorMagnitude = AnimData::GetPlayingAnimGroupMovementVectorMagnitude(animData, groupID_1);
                                   if (PlayingAnimGroupMovementVectorMagnitude != 0.0)
                                       v167 = (movementSpeedMult / PlayingAnimGroupMovementVectorMagnitude) * v167;
                                   AnimData::SetMovementSpeedMult(animData, v167);
                                   break;
                           }
                       }
                   }
                   else
                   {
                       if (groupID_1 != 255)
                       {
                           if (animGroup == kAnimGroup_TurnLeft || animGroup == kAnimGroup_TurnRight)
                           {
                               AnimData::SetMovementSpeedMult(animData, turnSpeed);
                           }
                           else if (animGroup < kAnimGroup_Forward || animGroup > kAnimGroup_TurnRight)
                           {
                               if (animGroup >= kAnimGroup_Equip && animGroup <= kAnimGroup_Counter)
                               {
                                   if (weap)
                                   {
                                       AnimMult = TESObjectWEAP::GetAnimMult(weap);
                                       ApplyPerkModifiers(ModifyAttackSpeed, this, weap, &AnimMult);
                                       if (!AnimGroup::IsAttack(animGroup) || TESObjectWEAP_IsMeleeWeapon(weap))
                                       {
                                           AnimData::SetRateOfFire(animData, AnimMult);
                                       }
                                       else
                                       {
                                           v66 = this->baseProcess->GetWeaponInfo();
                                           v67 = ContChangesEntry::HasWeaponMod(v66, kWeaponModEffect_IncreaseRateOfFire);
                                           AnimAttackMult = TESObjectWEAP::GetAnimAttackMult(weap, v67);
                                           v88 = AnimAttackMult * AnimMult;
                                           AnimData::SetRateOfFire(animData, v88);
                                       }
                                   }
                                   else
                                   {
                                       AnimData::SetRateOfFire(animData, 1.0);
                                   }
                               }
                           }
                           else
                           {
                               groupID_2 = groupID_1;
                               if (this->GetActorType())
                               {
                                   switch (AnimGroupID::GetGroupID(groupID_1)) {
                                       case kAnimGroup_Backward:
                                       case kAnimGroup_Left:
                                       case kAnimGroup_Right:
                                       case kAnimGroup_DodgeForward:
                                       case kAnimGroup_DodgeBack:
                                       case kAnimGroup_DodgeLeft:
                                       case kAnimGroup_DodgeRight:
                                           groupID_2 = ((groupID_1 & 0xFF00) | 3);
                                           break;
                                       case kAnimGroup_FastBackward:
                                       case kAnimGroup_FastLeft:
                                       case kAnimGroup_FastRight:
                                           groupID_2 = ((groupID_1 & 0xFF00) | 7);
                                           break;
                                       default:
                                           break;
                                   }
                               }
                               else
                               {
                                   groupID_2 = ((groupID_1 & 0xFF00) | 3);
                               }
                               v115 = AnimData::GetPlayingAnimGroupMovementVectorMagnitude(animData, groupID_2);
                               if (v115 != 0.0)
                                   v167 = (movementSpeedMult / v115) * v167;
                               AnimData::SetMovementSpeedMult(animData, v167);
                           }
                       }
                       v162 = g_animSequenceTypes[9 * animGroup];
                       currentPlayingAnimId = AnimData::GetNthSequenceGroupID(animData, v162);
                       if (currentPlayingAnimId != groupID_1 || !AnimData::GetAnimSequenceElement(animData, v162) || BSAnimGroupSequence::GetState(AnimData::GetAnimSequenceElement(animData, v162)) == kAnimState_Inactive)
                       {
                           if (AnimData::GetSequenceBaseFromMap(animData, groupID_1))
                           {
                               if (g_animSequenceTypes[9 * animGroup] == kSequence_Movement)
                               {
                                   if (AnimData::GetAnimSequenceElement(animData, kSequence_Movement))
                                   {
                                       v71 = AnimData::GetNthSequenceGroupID(animData, kSequence_Movement);
                                       if (animMoveType != AnimGroup::GetMoveType(v71))
                                       {
                                           v87 = (Actor::Process::GetByte12A(this) || Actor::Process::GetByte128(this));
                                           v72 = Anim_Concat_MoveType_HandType_Group_PowerArmor(animMoveType, animHandType, kAnimGroup_Idle, v87);
                                           v112 = AnimData::495740(animData, v72, 0);
                                           v73 = v112;
                                           if (v73 != AnimData::GetNthSequenceGroupID(animData, kSequence_Idle))
                                           {
                                               AnimData::PlayAnimGroup(animData, v112, 1, -1, -1);
                                               this->PlayFirstPersonAnimation();
                                           }
                                       }
                                   }
                               }
                               AnimData::PlayAnimGroup(animData, groupID_1, 1, -1, -1);
                               if (animAction != -1 && !AnimGroup::IsNonSpecialIdle(groupID_1))
                               {
                                   v74 = AnimData::GetAnimSequenceElement(animData, g_animSequenceTypes[9 * animGroup]);
                                   Actor::SetAnimActionAndSequence(this, animAction, v74);
                               }
                               this->PlayFirstPersonAnimation();
                               if (animGroup == kAnimGroup_JumpStart)
                               {
                                   a3 = kAnimGroup_JumpLoop;
                                   if ((moveFlags & (kMoveFlag_Right | kMoveFlag_Left | kMoveFlag_Backward | kMoveFlag_Forward)) != 0)
                                   {
                                       if ((moveFlags & kMoveFlag_Forward) != 0)
                                       {
                                           a3 = kAnimGroup_JumpLoopForward;
                                       }
                                       else if ((moveFlags & kMoveFlag_Backward) != 0)
                                       {
                                           a3 = kAnimGroup_JumpLoopBackward;
                                       }
                                       else if ((moveFlags & kMoveFlag_Left) != 0)
                                       {
                                           a3 = kAnimGroup_JumpLoopLeft;
                                       }
                                       else if ((moveFlags & kMoveFlag_Right) != 0)
                                       {
                                           a3 = kAnimGroup_JumpLoopRight;
                                       }
                                   }
                                   v86 = (Actor::Process::GetByte12A(this) || Actor::Process::GetByte128(this));
                                   v75 = Anim_Concat_MoveType_HandType_Group_PowerArmor(animMoveType, animHandType, a3, v86);
                                   groupID_1 = AnimData::495740(animData, v75, 0);
                                   AnimData::PlayAnimGroup(animData, groupID_1, 0, -1, -1);
                                   this->PlayFirstPersonAnimation();
                               }
                               else if (animGroup >= kAnimGroup_JumpLandForward && animGroup <= kAnimGroup_JumpLandRight && (moveFlags & (kMoveFlag_Right | kMoveFlag_Left | kMoveFlag_Backward | kMoveFlag_Forward)) != 0)
                               {
                                   groupID = kAnimGroup_Invalid;
                                   if ((moveFlags & kMoveFlag_Running) != 0)
                                   {
                                       if ((moveFlags & 1) != 0)
                                       {
                                           groupID = kAnimGroup_FastForward;
                                       }
                                       else if ((moveFlags & 2) != 0)
                                       {
                                           groupID = kAnimGroup_FastBackward;
                                       }
                                       else if ((moveFlags & 4) != 0)
                                       {
                                           groupID = kAnimGroup_FastLeft;
                                       }
                                       else if ((moveFlags & 8) != 0)
                                       {
                                           groupID = kAnimGroup_FastRight;
                                       }
                                   }
                                   else if ((moveFlags & 1) != 0)
                                   {
                                       groupID = kAnimGroup_Forward;
                                   }
                                   else if ((moveFlags & 2) != 0)
                                   {
                                       groupID = kAnimGroup_Backward;
                                   }
                                   else if ((moveFlags & 4) != 0)
                                   {
                                       groupID = kAnimGroup_Left;
                                   }
                                   else if ((moveFlags & 8) != 0)
                                   {
                                       groupID = kAnimGroup_Right;
                                   }
                                   if (groupID != kAnimGroup_Invalid)
                                   {
                                       v85 = (Actor::Process::GetByte12A(this) || Actor::Process::GetByte128(this));
                                       v76 = Anim_Concat_MoveType_HandType_Group_PowerArmor(animMoveType, animHandType, groupID, v85);
                                       groupID_1 = AnimData::495740(animData, v76, 0);
                                       AnimData::PlayAnimGroup(animData, groupID_1, 0, -1, -1);
                                       this->PlayFirstPersonAnimation();
                                   }
                               }
                           }
                       }
                       if (AnimData::GetAnimSequenceElement(animData, kSequence_Movement) && g_animSequenceTypes[9 * animGroup] != kSequence_Movement)
                       {
                           shouldEndSequence = 1;
                           if (currentAnimAction != -1)
                           {
                               v77 = this->baseProcess->GetCurrentSequence();
                               if (v77 == AnimData::GetAnimSequenceElement(animData, kSequence_Movement))
                                   shouldEndSequence = 0;
                           }
                           IdleAnimSequence_0 = AnimData::GetIdleAnimSequence_0(animData);
                           if (IdleAnimSequence_0 == AnimData::GetAnimSequenceElement(animData, kSequence_Movement))
                               shouldEndSequence = 0;
                           v79 = AnimData::GetAnimSequenceElement(animData, kSequence_Movement);
                           if (BSAnimGroupSequence::GetState(v79) != kAnimState_Animating)
                               shouldEndSequence = 0;
                           if (shouldEndSequence)
                           {
                               AnimData::EndsSequenceIfNotAim(animData, kSequence_Movement, 0);
                               if (this == g_thePlayer)
                               {
                                   v80 = PlayerCharacter::GetAnimData(g_thePlayer, kPlayerAnimData_1st);
                                   AnimData::EndsSequenceIfNotAim(v80, kSequence_Movement, 0);
                               }
                           }
                       }
                       if (AnimData::GetAnimSequenceElement(animData, kSequence_Weapon))
                       {
                           v81 = AnimData::GetNthSequenceGroupID(animData, kSequence_Weapon);
                           if (AnimGroup::IsAttack(v81))
                           {
                               v82 = sub_8A5340(this, &v107, 0);
                               this->baseProcess->Unk_117();
                           }
                       }
                   }
               }
           }
       }
   }
}
